# Models

Select a model with `python -m patch --model MODEL` or `/model MODEL` in chat.
`python -m patch --list-models QUERY` lists matching known names. Aliases such as
`sonnet` are defined in [the model module](../models.py); they can change over time.

## API keys

Use provider environment variables such as `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
`GEMINI_API_KEY`, or `OPENROUTER_API_KEY`. Alternatively use
`--api-key anthropic=YOUR_KEY` (substitute your provider). Shell history and process
listings can expose command-line keys, so prefer a private environment or `.env`.
Never commit credentials or paste them into issue reports.

A repository's own `.env` can still set keys, but not the variables that decide
where requests go. See
[repository configuration is untrusted](config.md#repository-configuration-is-untrusted).

Examples of model selection:

```bash
python -m patch --model sonnet
python -m patch --model openrouter/anthropic/claude-3.5-sonnet
python -m patch --model ollama_chat/YOUR_LOCAL_MODEL
```

For Ollama, start its server and pull the model first; set `OLLAMA_API_BASE` if
needed. For an OpenAI-compatible server use an `openai/` model name and configure
`OPENAI_API_BASE` and `OPENAI_API_KEY` as required by that server. Set these
endpoint variables in your shell environment, `~/.env`, or an `--env-file` you
name: Patch ignores them when the repository's own `.env` supplies them.
Availability, prices, permissions, and context limits are controlled by the
provider.

## Model warnings

Unknown context limits or token costs mean Patch lacks model metadata, not
necessarily that the model cannot work. Check the provider's model name and limits.
Add metadata with `.patch.model.metadata.json` or `--model-metadata-file`, from
the repository or your home directory: metadata describes a model, it does not
route requests.
The JSON maps model names to LiteLLM metadata such as `max_input_tokens`,
`max_output_tokens`, `input_cost_per_token`, `output_cost_per_token`,
`litellm_provider`, and `mode`.

## Model settings

Use `~/.patch.model.settings.yml` or `--model-settings-file` for a YAML list of
settings. Because `extra_params` can name an endpoint, Patch reads a
`.patch.model.settings.yml` inside the repository only with `--trust-repo-config`
or when you pass its path to `--model-settings-file`. For example:

```yaml
- name: openai/your-model
  edit_format: whole
  weak_model_name: null
  use_repo_map: true
```

See [the packaged settings](../resources/model-settings.yml) for supported examples.
These are distinct from model metadata. Use `--alias short:provider/model` to
define a short name. See [configuration](config.md) for storing command options.

## Edit formats

Patch chooses an edit format from its model settings. `diff` uses SEARCH/REPLACE
blocks; `whole` replaces full files; `udiff` uses unified diffs; `patch` uses
explicit patch operations. `--edit-format FORMAT` overrides the default.
Choose a format your model follows reliably. Use `/ask` for discussion without
edits and `/architect` for a plan followed by a separate editor model.
