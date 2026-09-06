# Patch changelog

Patch starts with a clean changelog as a fork of Aider.
For the inherited release history, see [the previous changelog](HISTORY.md).

## Unreleased

### Added

- Added repository-wide agent guidance in `AGENTS.md` and a contributor policy requiring documentation review and updates after every change, including changelog entries and preservation of upstream history.

### Changed

- Show a terminal notice with the available version and upgrade command when a newer `patch-code` release is available. Reuse successful checks for 24 hours, keep showing cached notices on launch, and leave installation to the user. Failed checks do not interrupt normal startup.
- Rebranded the application, browser UI, logo, and documentation from Aider to Patch.
- Adopted a centered single-tile SVG logo with a mint plus-shaped cutout and white Patch wordmark for the README and website, replacing the old terminal-font logo and its generator.
- Renamed the PyPI distribution to `patch-code` and the Python package and command to `patch`. Patch can also be launched with `python -m patch` to avoid conflicts with the Unix `patch` utility.
- Renamed configuration and state files from `.aider*` to `.patch*`, and environment variables from `AIDER_*` to `PATCH_*`. Existing Aider configuration is not migrated automatically and must be renamed and reviewed before use.
- Updated imports, filenames, tests, developer scripts, installation and upgrade commands, and repository links for the Patch fork. Preserved upstream attribution, historical records, and relevant upstream documentation links.
- Started a separate Patch changelog while retaining the inherited release history.

### Fixed

- Fixed Python 3.10 installation of the help and browser extras by generating dependency pins with Python and platform markers across the supported environments. Added regression checks for consistent pins across base and optional dependencies.
- Fixed Black formatting in the release-history helper so pre-commit checks pass.
- Included Python subpackages, model metadata and settings, tree-sitter queries, and help documentation in the built package.

### Removed

- Removed six GitHub Actions workflows: automated issue processing, daily PyPI version checks on Linux and Windows, GitHub Pages deployment, and Docker build and release publishing. Retained Linux and Windows tests, pre-commit checks, and PyPI releases; Docker and website sources remain available for manual builds.
- Removed the inherited `aider.chat` custom-domain declaration and upstream popularity statistics and testimonials from the Patch homepage and README.
