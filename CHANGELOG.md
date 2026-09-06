# Changelog

All notable changes to Patch will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Patch is a fork of Aider. Upstream releases and achievements are preserved
separately in [HISTORY.md](HISTORY.md).

## [Unreleased]

### Changed

- Adopt Keep a Changelog formatting and document the Semantic Versioning policy
  for future releases.

### Security

- Require both `*** Begin Patch` and `*** End Patch` before applying a
  `patch`-format response, so one that was cut off is sent back to the model
  instead of half applied. Prose before or after the patch is now ignored rather
  than breaking the parse.
- Reject a `whole`-format response whose file listing was never closed instead of
  replacing the file with the part that arrived, and ask the model to send the file
  again. Live previews stay permissive.
- Authorize the destination of a `patch`-format move, not just its source, and ask
  separately before overwriting a file that already exists there. `--yes-always`
  does not answer that question. A move onto a read-only file, or one that resolves
  outside the project, is refused.
- Refuse model-requested edits to paths that resolve outside the project, whether
  through `../` segments or an absolute path, and report the resolved location.
  Files you added yourself stay editable wherever they are. Previously such a path
  was treated as an ordinary new or non-chat file, which `--yes-always` approved
  automatically.
- Ignore the settings in a repository's own `.patch.conf.yml`, `.env`, and model
  settings files that run commands, carry credentials, steer API traffic, redirect
  telemetry, write outside the repository, or answer prompts. Cloning a repository
  and letting Patch edit a file no longer runs a command of the repository's
  choosing or sends requests to an endpoint it names. The same settings still work
  from your own configuration, from a `--config`, `--env-file`, or
  `--model-settings-file` path you name, and from `--trust-repo-config` for a
  repository you trust.
- Store the repo map tags cache in `~/.patch/caches/`, keyed by a hash of the
  repository path, instead of inside the repository, and read it as JSON that is
  validated before use. A repository can no longer ship a cache whose pickled
  values run during a repo map scan, and a corrupt entry is now a cache miss.
  `PATCH_TAGS_CACHE_DIR` relocates the cache; old `.patch.tags.cache.v*`
  directories are unused and can be deleted.
- Bind the `--browser` GUI to `127.0.0.1` instead of every network interface, and
  give each browser session its own state and coder so sessions can no longer read
  or corrupt one another's chat history, files, and undo state. Set
  `PATCH_GUI_ADDRESS` to listen elsewhere; Patch warns when that address is not
  loopback.

### Fixed

- Write edited files by renaming a complete temporary file over the old one, so a
  write that fails part-way leaves the previous file intact instead of an empty or
  half-written one. Permissions are preserved, symlinks still update their target,
  and where the rename is refused, as on Windows when another process holds the
  file open, Patch writes in place as before.
- Let the `patch` format add a file. Authorizing a new file creates an empty
  placeholder, which the ADD action then rejected as an existing file, so every add
  failed and left an empty file behind.
- Apply an edit that empties a file instead of reporting it as a block that failed
  to match, which also stopped the `diff` format from trying the same edit against
  another file in the chat.
- Report and commit only the files an edit actually changed. When applying a
  response failed part-way, every file it mentioned was reported as edited and
  auto-committed, which could sweep in unrelated changes to a file Patch never
  wrote.
- Keep `--dry-run` from creating the files an edit would have added. The
  `diff` and `udiff` formats created an empty file while working out the new
  content, which ran before the edit was authorized, so a declined or dry-run
  edit left a zero-byte file behind.
- Scrub ambient provider credentials in the `main()` tests, which otherwise decided
  which model was selected and sent a live OpenRouter tier request with the
  developer's own key.
- Use a local HTTP fixture for scraper tests instead of a public site that can
  return bot challenges, and install Pandoc before CI tests to avoid runtime
  download failures on Windows.
- Make update-cache tests independent of filesystem clock resolution and cover
  fresh, expired, and future-dated cache boundaries.

## [0.1.0] - 2026-09-06

First release under the Patch identity. Supports Python 3.10–3.14.

### Added

- Seven packaged Markdown guides for interactive `/help`, covering installation,
  usage, configuration, models, Git, troubleshooting, and analytics.
- Terminal update notices with an upgrade command and a 24-hour cache for successful
  checks. Updates are never installed automatically.
- Patch wordmark and icon, contributor documentation, and repository-wide agent guidance.
- Regression checks for dependency compatibility across supported Python versions
  and for consistent runtime and package versions.

### Changed

- Rename the distribution to `patch-code`, the Python module and CLI to `patch`,
  configuration/state files to `.patch*`, and application variables to `PATCH_*`.
  Existing Aider settings require manual migration; provider credential names
  such as `OPENAI_API_KEY` remain unchanged.
- Use `patch/__init__.py` as the single version source for runtime and package metadata.
- Point documentation and support links at Patch's GitHub repository. Use a separate
  help cache and an inline browser favicon instead of inherited website resources.
- Preserve historical Aider benchmark datasets under `benchmark/data/` and write
  generated plots to `tmp.benchmarks/`, retaining upstream attribution.
- Generate dependency locks with Python and platform markers across Python 3.10–3.14.
- Make PyPI publishing manual-only; branch and tag pushes do not publish packages.

### Fixed

- Resolve installation of help and browser extras on Python 3.10.
- Include Python subpackages, model resources, tree-sitter queries, and help docs
  in built distributions.
- Remove the inherited version floor that caused runtime and package metadata to disagree.
- Correct contributor paths, CI matrix documentation, stale audit statuses, and the
  unused OAuth declaration that caused a flake8 failure.
- Restore legitimate Aider attribution and replace inherited-site URLs with upstream
  GitHub source links. Keep fixture replacements consistent and whitespace intact.

### Removed

- The inherited website, Jekyll configuration, website-only generators, and their
  unused development dependencies.
- Default analytics destinations and unsolicited opt-in prompts. User-configured
  PostHog telemetry and local event logging remain available; automatic exception
  capture is disabled.
- Inherited issue-processing, scheduled version-check, GitHub Pages, and Docker
  publishing workflows, plus automatic PyPI publishing on tag pushes.
- Upstream popularity claims presented as Patch achievements and fabricated Patch
  legal-entity/domain references.

[Unreleased]: https://github.com/PierrunoYT/patch/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/PierrunoYT/patch/releases/tag/v0.1.0
