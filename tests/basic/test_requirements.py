from pathlib import Path

import pytest
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


@pytest.mark.parametrize("python_version", ["3.10", "3.11", "3.12", "3.13", "3.14"])
@pytest.mark.parametrize("platform", ["linux", "win32"])
def test_dependency_pins_agree_across_extras(python_version, platform):
    root = Path(__file__).resolve().parents[2]
    environment = default_environment()
    environment.update(
        python_version=python_version,
        python_full_version=python_version + ".0",
        sys_platform=platform,
        platform_system="Windows" if platform == "win32" else "Linux",
        platform_machine="AMD64" if platform == "win32" else "x86_64",
    )
    files = [root / "requirements.txt", root / "requirements/common-constraints.txt"]
    files += sorted((root / "requirements").glob("requirements-*.txt"))
    pins = {}
    for path in files:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            requirement = Requirement(line)
            if requirement.marker and not requirement.marker.evaluate(environment):
                continue
            name = canonicalize_name(requirement.name)
            pin = str(requirement.specifier)
            if name in pins:
                assert pin == pins[name], f"Conflicting {name} pin in {path.name}: {pin}"
            pins[name] = pin

    assert pins["numpy"].startswith("==1." if python_version == "3.10" else "==2.")
