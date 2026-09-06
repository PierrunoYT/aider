import os
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import packaging.version

import patch
from patch import utils
from patch.dump import dump  # noqa: F401

VERSION_CHECK_FNAME = Path.home() / ".patch" / "caches" / "versioncheck"


def install_from_main_branch(io):
    """
    Install the latest version of patch from the main branch of the GitHub repository.
    """

    return utils.check_pip_install_extra(
        io,
        None,
        "Install the development version of patch from the main branch?",
        ["git+https://github.com/PierrunoYT/patch.git"],
        self_update=True,
    )


def install_upgrade(io):
    """
    Install the latest version of patch from PyPI.
    """

    new_ver_text = "Install latest version of Patch?"

    docker_image = os.environ.get("PATCH_DOCKER_IMAGE")
    if docker_image:
        text = f"""
{new_ver_text} To upgrade, run:

    docker pull {docker_image}
"""
        io.tool_warning(text)
        return True

    success = utils.check_pip_install_extra(
        io,
        None,
        new_ver_text,
        ["patch-code"],
        self_update=True,
    )

    if success:
        io.tool_output("Re-run patch to use new version.")
        sys.exit()

    return


def check_version(io, just_check=False, verbose=False):
    latest_version = None
    if not just_check:
        try:
            since = time.time() - VERSION_CHECK_FNAME.stat().st_mtime
            if 0 <= since < 24 * 60 * 60:
                latest_version = str(
                    packaging.version.Version(VERSION_CHECK_FNAME.read_text().strip())
                )
        except (OSError, ValueError):
            # Also handles the empty timestamp-only cache used by older versions.
            pass

    if latest_version is None:
        # To keep startup fast, avoid importing this unless needed.
        import requests

        try:
            response = requests.get("https://pypi.org/pypi/patch-code/json", timeout=3)
            response.raise_for_status()
            latest_version = str(packaging.version.Version(response.json()["info"]["version"]))
        except (requests.RequestException, ValueError, KeyError, TypeError) as err:
            if just_check or verbose:
                io.tool_error(f"Unable to check for Patch updates: {err}")
            return False

        try:
            VERSION_CHECK_FNAME.parent.mkdir(parents=True, exist_ok=True)
            VERSION_CHECK_FNAME.write_text(latest_version)
        except OSError:
            # A read-only cache must not prevent the notice or normal startup.
            pass

    # Compare the installed distribution, not the inherited upstream fallback version.
    try:
        current_version = version("patch-code")
    except PackageNotFoundError:
        current_version = patch.__version__

    try:
        is_update_available = packaging.version.parse(latest_version) > packaging.version.parse(
            current_version
        )
    except ValueError as err:
        if just_check or verbose:
            io.tool_error(f"Unable to compare Patch versions: {err}")
        return False

    if just_check or verbose:
        io.tool_output(f"Current version: {current_version}")
        io.tool_output(f"Latest version: {latest_version}")
        if is_update_available:
            io.tool_output("Update available")
        else:
            io.tool_output("No update available")

    if just_check:
        return is_update_available

    if not is_update_available:
        return False

    io.tool_warning(f"Patch update available: {current_version} → {latest_version}")
    docker_image = os.environ.get("PATCH_DOCKER_IMAGE")
    if docker_image:
        io.tool_output(f"To update, run: docker pull {docker_image}")
    else:
        io.tool_output("To update, run: python -m patch --upgrade")
    return True
