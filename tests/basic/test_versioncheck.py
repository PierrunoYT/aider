import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from patch import versioncheck


@pytest.fixture
def update_check(tmp_path, monkeypatch):
    cache = tmp_path / "versioncheck"
    monkeypatch.setattr(versioncheck, "VERSION_CHECK_FNAME", cache)
    monkeypatch.delenv("PATCH_DOCKER_IMAGE", raising=False)
    io = MagicMock()
    with (
        patch("patch.versioncheck.version", return_value="0.1.0"),
        patch("requests.get") as get,
        patch("patch.versioncheck.install_upgrade") as install,
    ):
        get.return_value.json.return_value = {"info": {"version": "0.2.0"}}
        yield io, cache, get
        install.assert_not_called()
        io.confirm_ask.assert_not_called()


def test_notice_on_launch_and_from_cache(update_check):
    io, cache, get = update_check
    assert versioncheck.check_version(io) is True
    io.tool_warning.assert_called_once_with("Patch update available: 0.1.0 → 0.2.0")
    io.tool_output.assert_called_with("To update, run: python -m patch --upgrade")
    get.assert_called_once_with("https://pypi.org/pypi/patch-code/json", timeout=3)
    assert cache.read_text() == "0.2.0"

    io.reset_mock()
    assert versioncheck.check_version(io) is True
    io.tool_warning.assert_called_once()
    assert get.call_count == 1


@pytest.mark.parametrize("latest", ["0.1.0", "0.0.9", "0.1.0rc1"])
def test_no_notice_when_not_newer(update_check, latest):
    io, cache, get = update_check
    get.return_value.json.return_value = {"info": {"version": latest}}
    assert versioncheck.check_version(io) is False
    io.tool_warning.assert_not_called()


@pytest.mark.parametrize("contents", ["", "invalid", "0.1.0"])
def test_legacy_invalid_or_expired_cache_is_refreshed(update_check, contents):
    io, cache, get = update_check
    cache.write_text(contents)
    if contents == "0.1.0":
        os.utime(cache, (0, 0))
    assert versioncheck.check_version(io) is True
    get.assert_called_once()


def test_explicit_check_bypasses_cache(update_check):
    io, cache, get = update_check
    cache.write_text("0.1.0")
    assert versioncheck.check_version(io, just_check=True) is True
    get.assert_called_once()
    io.tool_output.assert_any_call("Update available")


@pytest.mark.parametrize("error", [requests.Timeout(), requests.HTTPError(), ValueError()])
def test_failed_check_does_not_interrupt_startup_or_cache_failure(update_check, error):
    io, cache, get = update_check
    get.side_effect = error
    assert versioncheck.check_version(io) is False
    assert not cache.exists()
    io.tool_error.assert_not_called()
    assert versioncheck.check_version(io, just_check=True) is False
    io.tool_error.assert_called_once()


def test_read_only_cache_does_not_hide_notice(update_check):
    io, cache, get = update_check
    with patch("pathlib.Path.write_text", side_effect=PermissionError):
        assert versioncheck.check_version(io) is True
    io.tool_warning.assert_called_once()


def test_docker_notice(update_check, monkeypatch):
    io, cache, get = update_check
    monkeypatch.setenv("PATCH_DOCKER_IMAGE", "example/patch:latest")
    assert versioncheck.check_version(io) is True
    io.tool_output.assert_called_with("To update, run: docker pull example/patch:latest")


def test_uninstalled_source_checkout_uses_module_version(update_check, monkeypatch):
    io, cache, get = update_check
    monkeypatch.setattr(versioncheck.patch, "__version__", "0.2.0")
    with patch("patch.versioncheck.version", side_effect=versioncheck.PackageNotFoundError):
        assert versioncheck.check_version(io) is False
