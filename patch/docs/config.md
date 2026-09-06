# Configuration

Run `python -m patch --help` for the complete, current CLI option reference.
Most options also accept `.patch.conf.yml` entries or `PATCH_*` environment variables.
For example, `--dark-mode`, `dark-mode: true` in YAML, and `PATCH_DARK_MODE=true`
are equivalent. Command-line values override environment and configuration values.

Patch searches for `.patch.conf.yml` in your home directory, Git repository root,
and current directory, with nearer configuration taking precedence. Use
`--config FILE` for an explicit configuration file.

```yaml
model: sonnet
dark-mode: true
auto-commits: false
```

## Environment and credentials

Provider credentials retain their own names, such as `ANTHROPIC_API_KEY` and
`OPENAI_API_KEY`. Store them in your shell environment or an untracked `.env` file.
Use `--env-file FILE` to select an environment file. YAML `api-key` entries and
`--api-key provider=KEY` also support providers beyond OpenAI and Anthropic.
`--set-env NAME=value` sets other provider variables.

Review repository-local YAML and `.env` files before running Patch: they can
configure executable commands and provider endpoints. Never load untrusted
repository settings with credentials present.

## Linting and tests

Patch can automatically lint edited files (`--auto-lint`, enabled by default).
Configure `--lint-cmd COMMAND` or `--lint-cmd 'python: COMMAND'`. Use
`--test-cmd COMMAND` with `--auto-test` for automatic tests, or `/test COMMAND`
inside chat. Only configure trusted commands.

## State and privacy

Patch uses `.patch*` state files and `~/.patch/` for user-level data and caches.
The repo map cache lives in `~/.patch/caches/`, keyed by a hash of the repository
path, so a repository never supplies its own cache; `PATCH_TAGS_CACHE_DIR` moves it
elsewhere. Any `.patch.tags.cache.v*` directory left by an earlier version is unused
and safe to delete. `--input-history-file` and `--chat-history-file` change history
destinations.
History, logs, and verbose settings can contain sensitive data; do not publish them
without review. Patch does not migrate `.aider*` or `AIDER_*` settings automatically.
See [analytics](analytics.md) for the disabled-by-default telemetry instrumentation.
