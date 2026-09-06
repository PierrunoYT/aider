import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml
from packaging.version import Version

import patch


def test_version_ignores_legacy_scm_module(monkeypatch):
    monkeypatch.setitem(sys.modules, "patch._version", SimpleNamespace(__version__="0.86.3.dev"))
    namespace = runpy.run_path(patch.__file__)
    assert namespace["__version__"] == patch.__version__
    assert str(Version(namespace["__version__"])) == namespace["__version__"]
    assert namespace["__all__"] == ["__version__"]


def test_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "patch", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == f"patch {patch.__version__}"


def test_release_is_manual_only():
    root = Path(__file__).resolve().parents[2]
    workflow = yaml.load(
        (root / ".github/workflows/release.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert set(workflow["on"]) == {"workflow_dispatch"}
