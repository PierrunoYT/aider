# Agent guidance for Patch

This file applies to the entire repository. See [CONTRIBUTING.md](CONTRIBUTING.md)
for development setup and contribution guidelines.

## Project identity

- The fork is **Patch**, the PyPI distribution is `patch-code`, and the Python
  package and CLI are `patch`. Prefer `python -m patch` in instructions to avoid
  conflicts with the Unix `patch` utility.
- Use `.patch*` for application configuration/state and `PATCH_*` for application
  environment variables.
- Preserve genuine upstream Aider attribution, historical benchmark results,
  license notices, and useful upstream GitHub documentation links. Do not relabel
  upstream achievements or invent Patch domains.

## Code and dependencies

- Runtime code lives in `patch/`, tests in `tests/`, packaged Markdown documentation
  in `patch/docs/`, and developer tooling in `scripts/`. There is no website build.
- Support Python 3.10 through 3.14, as declared in `pyproject.toml`.
- Follow existing patterns, keep changes focused, and do not add type hints.
- Use the configured isort, Black (100 columns, preview mode), flake8, and
  codespell hooks rather than manually reproducing their formatting.
- Edit dependency sources under `requirements/*.in`, then regenerate locks with
  `./scripts/pip-compile.sh` (requires `uv`). Do not hand-edit generated pins.
  Preserve universal Python/platform compatibility across base and optional extras.

## Documentation after every change (required)

- After every change, review all documentation for impact and update every
  affected document in the same change. Documentation is part of completion,
  not a follow-up task. Do not make cosmetic edits to unaffected documents.
- Check the README, contributor guide, this file, packaged docs under
  `patch/docs/`, and relevant component READMEs in `benchmark/`, `docker/`,
  and other affected directories. Keep duplicated instructions consistent.
- Update examples, CLI help, configuration/environment-variable references,
  installation and upgrade instructions, and generated documentation whenever
  the corresponding behavior changes. Verify affected commands and links.
- Record changes under `Unreleased` in [CHANGELOG.md](CHANGELOG.md). Use the
  appropriate category and explain user-visible behavior or contributor impact.
  Do not add Patch entries to inherited `HISTORY.md` files or rewrite upstream history.
- Keep packaged Markdown and `python -m patch --help` consistent. Never regenerate
  inherited history or commit personal analytics, credentials, or private
  conversation data.
- If no documentation beyond the changelog needs updating, state that in the
  completion summary and explain why.

## Verification and handoff

- Add or update regression tests for behavior changes. Run focused tests with
  `pytest tests/basic/test_<module>.py`; run `pytest` for broader changes after
  installing the necessary development and optional dependencies.
- Run `pre-commit run --all-files` before handing off changes. For documentation-only
  changes, check spelling, links, and relevant examples; runtime tests are not needed.
- Inspect the final diff for unrelated edits, generated-file drift, and sensitive
  data. Preserve changes made by others.
- Report what changed, which documentation was updated, and the checks actually
  run. Explicitly disclose any failures or verification limitations.
- Do not push, publish a package, or trigger a release without user authorization.
