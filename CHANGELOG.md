# Patch changelog

Patch starts with a clean changelog as a fork of Aider.
For the inherited release history, see [the previous changelog](HISTORY.md).

## Unreleased

## 0.1.0 — 2026-09-06

### Added

- Added repository-wide agent guidance in `AGENTS.md` and a contributor policy requiring documentation review and updates after every change, including changelog entries and preservation of upstream history.

### Changed

- Prepared the first Patch release as `0.1.0`. Runtime and distribution metadata now share the version in `patch/__init__.py`, independent of Git tags or inherited Aider version floors.
- Replaced the inherited website with seven packaged Markdown guides in `patch/docs/`, preserving `/help <question>` and linking runtime help to retained GitHub docs and anchors. A separate help cache avoids reusing the former website index. The browser uses an emoji favicon instead of a remote site asset.
- Moved the two historical Aider datasets used by benchmark tools into `benchmark/data/` without changing results, and redirected plot output to `tmp.benchmarks/`. Updated the README, contributor guide, agent guidance, benchmark instructions, and stale audit statuses for the site removal and recent fixes.
- Replaced inherited-site links in release history with upstream GitHub source links, preserving Aider attribution. Replaced fixture domains with `example.org` consistently in the input and expected output without altering whitespace.
- Ignored local coding-agent settings (`.claude/`, `.codex/`, `.gemini/`) and third-party tool state (`.open-edit/`) so they stay out of the repository. Session-start hooks are a per-developer choice and should not run automatically for everyone who clones.
- Show a terminal notice with the available version and upgrade command when a newer `patch-code` release is available. Reuse successful checks for 24 hours, keep showing cached notices on launch, and leave installation to the user. Failed checks do not interrupt normal startup.
- Rebranded the application, browser UI, logo, and documentation from Aider to Patch.
- Adopted matching hand-coded SVG logos in the root `assets/` folder: a 2048 × 2048 P-only icon (`assets/logo-icon.svg`) and a wide PATCH-only wordmark with no separate icon (`assets/logo.svg`). Updated the README to display the wordmark and link both logos. Both use mint geometric shapes on charcoal, equal side margins, and font-independent vector paths, replacing the earlier plus-tile design and old terminal-font generator.
- Renamed the PyPI distribution to `patch-code` and the Python package and command to `patch`. Patch can also be launched with `python -m patch` to avoid conflicts with the Unix `patch` utility.
- Renamed configuration and state files from `.aider*` to `.patch*`, and environment variables from `AIDER_*` to `PATCH_*`. Existing Aider configuration is not migrated automatically and must be renamed and reviewed before use.
- Updated imports, filenames, tests, developer scripts, installation and upgrade commands, and repository links for the Patch fork. Preserved upstream attribution, historical records, and relevant upstream documentation links.
- Started a separate Patch changelog while retaining the inherited release history.

### Fixed

- Corrected the contributor guide, which still described Python 3.9–3.12 CI, a `patch/tests` directory, and requirement files at paths that do not exist. It now matches the 3.10–3.14 test matrix, the real `tests` directory, and the `requirements/` layout. Updated the installation page to prefer `python -m patch` and to state the supported Python range, and recorded the resolved and partially resolved findings in `AUDIT.md`.
- Regenerated the documentation that is derived from the CLI parser, which had not been refreshed when the `--check-update` help text changed. The options reference, YAML and `.env` guides, and the sample configuration assets now match `patch --help`. Also refreshed the supported-languages table, which was missing repo-map support for bash.
- Replaced links that presented upstream Aider's Discord as the Patch community with links to this repository's issue tracker, across the website navigation, footer, homepage, and help include. Relabelled the LLM leaderboards link as Aider's, and pointed the homepage release-notes link at this repository's own history page.
- Removed the fabricated "Patch AI LLC" entity and `patch.chat` domain introduced by the rebrand. The inherited contributor agreement and privacy policy are restored to upstream Aider AI LLC and labelled as retained upstream documents, the FAQ explains that Patch is an unaffiliated fork with no legal entity, and the cookie banner no longer scopes itself to a nonexistent domain. Repaired the remaining `patch-ai/patch` links in the analytics documentation.
- Pointed the analytics opt-in prompt at Patch's own analytics documentation instead of the upstream page, and cleared the inherited website analytics key so the documentation site cannot report to upstream either.
- Restored upstream Aider attribution in the inherited release history and FAQ. The rebrand had rewritten upstream entries to read as Patch achievements, including the per-release code-authorship percentages. `HISTORY.md` and its website copy now state that they are inherited Aider history, and the FAQ presents the authorship statistics and model-usage table as upstream data. Repaired two documentation links that pointed at a nonexistent `patch-ai/patch` repository and at a renamed upstream anchor.
- Fixed Python 3.10 installation of the help and browser extras by generating dependency pins with Python and platform markers across the supported environments. Added regression checks for consistent pins across base and optional dependencies.
- Fixed Black formatting in the release-history helper.
- Fixed the flake8 `F824` failure that kept `pre-commit run --all-files` failing on the tree: the OAuth callback handler declared `nonlocal server_error` in `do_GET` without ever assigning it.
- Included Python subpackages, model metadata and settings, tree-sitter queries, and help documentation in the built package.

### Removed

- Removed automatic PyPI publishing on tag pushes. The release workflow now runs only through an explicit manual dispatch.
- Deleted the inherited website, Jekyll build configuration, website-only generators for badges, blame, icons, audio, and inherited history, and their unused development dependencies. Help and documentation URL tests now run without remote model downloads or HTTP requests; packaged-doc changes are covered by CI.
- Removed all analytics collection. The inherited Mixpanel and PostHog project keys belonged to upstream Aider, so Patch now ships no analytics destination at all: no events are sent, and the opt-in prompt no longer appears, including for the random subset of users upstream would have asked. The instrumentation remains usable for your own telemetry — the PostHog client is only created when you pass `--analytics-posthog-project-api-key`, and `--analytics-log` still writes events to a local file without sending them. Automatic exception capture, which bypassed the redaction applied to normal events, is now off.
- Removed six GitHub Actions workflows: automated issue processing, daily PyPI version checks on Linux and Windows, GitHub Pages deployment, and Docker build and release publishing. Retained Linux and Windows tests, pre-commit checks, and PyPI releases; Docker sources remain available for manual builds.
- Removed the inherited custom-domain declaration and upstream popularity statistics and testimonials from the Patch homepage and README.
