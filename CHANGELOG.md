# Patch changelog

Patch starts with a clean changelog as a fork of Aider.
For the inherited release history, see [the previous changelog](HISTORY.md).

## Unreleased

### Added

- Added repository-wide agent guidance in `AGENTS.md` and a contributor policy requiring documentation review and updates after every change, including changelog entries and preservation of upstream history.

### Changed

- Show a terminal notice with the available version and upgrade command when a newer `patch-code` release is available. Reuse successful checks for 24 hours, keep showing cached notices on launch, and leave installation to the user. Failed checks do not interrupt normal startup.
- Rebranded the application, browser UI, logo, and documentation from Aider to Patch.
- Adopted matching hand-coded SVG logos in the root `assets/` folder: a 2048 × 2048 P-only icon (`assets/logo-icon.svg`) and a wide PATCH-only wordmark with no separate icon (`assets/logo.svg`). Updated the README to display the wordmark and link both logos; retained matching copies in `patch/website/assets/` for the website. Both use mint geometric shapes on charcoal, equal side margins, and font-independent vector paths, replacing the earlier plus-tile design and old terminal-font generator.
- Renamed the PyPI distribution to `patch-code` and the Python package and command to `patch`. Patch can also be launched with `python -m patch` to avoid conflicts with the Unix `patch` utility.
- Renamed configuration and state files from `.aider*` to `.patch*`, and environment variables from `AIDER_*` to `PATCH_*`. Existing Aider configuration is not migrated automatically and must be renamed and reviewed before use.
- Updated imports, filenames, tests, developer scripts, installation and upgrade commands, and repository links for the Patch fork. Preserved upstream attribution, historical records, and relevant upstream documentation links.
- Started a separate Patch changelog while retaining the inherited release history.

### Fixed

- Replaced links that presented upstream Aider's Discord as the Patch community with links to this repository's issue tracker, across the website navigation, footer, homepage, and help include. Relabelled the LLM leaderboards link as Aider's, and pointed the homepage release-notes link at this repository's own history page.
- Removed the fabricated "Patch AI LLC" entity and `patch.chat` domain introduced by the rebrand. The inherited contributor agreement and privacy policy are restored to upstream Aider AI LLC and labelled as retained upstream documents, the FAQ explains that Patch is an unaffiliated fork with no legal entity, and the cookie banner no longer scopes itself to a nonexistent domain. Repaired the remaining `patch-ai/patch` links in the analytics documentation.
- Documented that Patch still ships upstream Aider's PostHog project key, so opted-in analytics are reported to the upstream project, and pointed the opt-in prompt at Patch's own analytics documentation instead of the upstream page. Cleared the inherited website analytics key so the documentation site cannot report to upstream either.
- Restored upstream Aider attribution in the inherited release history and FAQ. The rebrand had rewritten upstream entries to read as Patch achievements, including the per-release code-authorship percentages. `HISTORY.md` and its website copy now state that they are inherited Aider history, and the FAQ presents the authorship statistics and model-usage table as upstream data. Repaired two documentation links that pointed at a nonexistent `patch-ai/patch` repository and at a renamed upstream anchor.
- Fixed Python 3.10 installation of the help and browser extras by generating dependency pins with Python and platform markers across the supported environments. Added regression checks for consistent pins across base and optional dependencies.
- Fixed Black formatting in the release-history helper so pre-commit checks pass.
- Included Python subpackages, model metadata and settings, tree-sitter queries, and help documentation in the built package.

### Removed

- Removed six GitHub Actions workflows: automated issue processing, daily PyPI version checks on Linux and Windows, GitHub Pages deployment, and Docker build and release publishing. Retained Linux and Windows tests, pre-commit checks, and PyPI releases; Docker and website sources remain available for manual builds.
- Removed the inherited `aider.chat` custom-domain declaration and upstream popularity statistics and testimonials from the Patch homepage and README.
