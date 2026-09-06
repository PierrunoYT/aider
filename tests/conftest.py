import os

import pytest

from patch import utils


@pytest.fixture(autouse=True)
def tags_cache_dir(tmp_path_factory):
    """Keep the repo map tags cache out of the user's home directory.

    RepoMap stores its cache per user rather than inside the repository, so
    without this every test that builds a coder would leave a cache behind in
    ~/.patch/caches.
    """

    previous = os.environ.get("PATCH_TAGS_CACHE_DIR")
    os.environ["PATCH_TAGS_CACHE_DIR"] = str(tmp_path_factory.mktemp("tags-cache"))

    yield

    if previous is None:
        os.environ.pop("PATCH_TAGS_CACHE_DIR", None)
    else:
        os.environ["PATCH_TAGS_CACHE_DIR"] = previous


@pytest.fixture(autouse=True)
def no_installing(request, monkeypatch):
    """Fail the test rather than installing packages into the environment.

    Several code paths offer to pip install an extra, and a test that reaches
    one of them would change the environment it is running in. Tests that mean
    to exercise the installer are marked with `installer`.
    """

    if request.node.get_closest_marker("installer"):
        return

    def refuse(cmd, *args, **kwargs):
        raise AssertionError(
            f"This test tried to install packages: {cmd}."
            " Mock the install, or mark the test with @pytest.mark.installer."
        )

    monkeypatch.setattr(utils, "run_install", refuse)
