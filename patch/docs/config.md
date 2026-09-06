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

## Repository configuration is untrusted

A cloned repository ships its own `.patch.conf.yml`, `.env`, and
`.patch.model.settings.yml`. Patch reads the ordinary settings from them, but
ignores the ones that run commands
(`lint-cmd`, `test-cmd`, `editor`, `notifications-command`, `load`, ...), carry
credentials or steer API traffic (`api-key`, `openai-api-base`, `set-env`,
`verify-ssl`, ...), redirect telemetry, write outside the repository
(`chat-history-file`, ...), or answer prompts for you (`yes-always`). It says
which settings it ignored. Repository model settings (`extra_params`, which can
name an endpoint) are skipped for the same reason, while model metadata, which
only describes context windows and costs, is still read. A repository `.env` is
loaded the same way: variables that redirect Patch, such as `*_API_BASE`,
`*_BASE_URL`, `PATCH_LINT_CMD` and the other `PATCH_*` names for the settings
above, `GIT_*`, `PATH`, and proxy or TLS settings, are skipped. Everything else
in it, including the variables your own tooling needs, is loaded as before.

Those settings still work from your own `~/.patch.conf.yml`, `~/.env`, a
`--config FILE` or `--env-file FILE` you name, the environment, and the command
line. To honor a specific repository's own configuration, run it with
`--trust-repo-config`.

## Environment and credentials

Provider credentials retain their own names, such as `ANTHROPIC_API_KEY` and
`OPENAI_API_KEY`. Store them in your shell environment or an untracked `.env` file.
A key obtained through the OpenRouter sign-in is written to
`~/.patch/oauth-keys.env`, which Patch keeps readable only by you.
Use `--env-file FILE` to select an environment file. YAML `api-key` entries and
`--api-key provider=KEY` also support providers beyond OpenAI and Anthropic.
`--set-env NAME=value` sets other provider variables.

Review repository-local YAML and `.env` files before running Patch with
`--trust-repo-config`: they can configure executable commands and provider
endpoints. Never trust an unreviewed repository's settings with credentials
present.

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
