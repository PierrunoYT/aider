import tomllib
from pathlib import Path

import pytest
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version


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


def read_project():
    root = Path(__file__).resolve().parents[2]
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]


def declared_requirements():
    project = read_project()
    requirements = list(project["dependencies"])
    for extra in project["optional-dependencies"].values():
        requirements.extend(extra)

    return [Requirement(text) for text in requirements]


def locked_versions():
    root = Path(__file__).resolve().parents[2]
    files = [root / "requirements.txt"]
    files += sorted((root / "requirements").glob("requirements-*.txt"))

    versions = {}
    for path in files:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            requirement = Requirement(line)
            for spec in requirement.specifier:
                if spec.operator == "==":
                    versions.setdefault(canonicalize_name(requirement.name), set()).add(
                        Version(spec.version)
                    )

    return versions


def test_published_metadata_names_only_direct_dependencies():
    # The published package declares direct dependencies, not the whole lock
    project = read_project()

    assert "dependencies" not in project["dynamic"]
    assert len(project["dependencies"]) < 60


def test_every_declared_dependency_is_locked_and_tested():
    versions = locked_versions()

    for requirement in declared_requirements():
        name = canonicalize_name(requirement.name)
        locked = versions.get(name)
        assert locked, f"{name} is declared in pyproject.toml but is not in any lock file"
        assert any(
            requirement.specifier.contains(version, prereleases=True) for version in locked
        ), f"No locked version of {name} satisfies {requirement.specifier}"


def test_every_direct_requirement_is_published():
    root = Path(__file__).resolve().parents[2]
    declared = {canonicalize_name(req.name) for req in declared_requirements()}

    for path in sorted((root / "requirements").glob("*.in")) + [
        root / "requirements/requirements.in"
    ]:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            name = canonicalize_name(Requirement(line).name)
            assert name in declared, f"{name} from {path.name} is missing from pyproject.toml"
