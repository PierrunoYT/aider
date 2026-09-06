import os

import pytest


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
