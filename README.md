<p align="center">
  <img src="assets/logo.svg" alt="PATCH wordmark" width="300">
</p>

<h1 align="center">Patch</h1>

<p align="center">
  <strong>AI pair programming in your terminal.</strong><br>
  Work with your codebase. Make changes with an LLM. Review them with Git.
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="CHANGELOG.md">Changelog</a> ·
  <a href="https://github.com/PierrunoYT/patch/issues">Report an issue</a>
</p>

Patch is a command-line coding assistant that helps you build features, fix bugs,
and navigate existing projects using cloud or local language models. It maps your
repository for context, edits files directly, and integrates with your Git workflow.

## Features

- **Choose your model.** Connect to cloud providers or local models.
- **Work across your codebase.** Use a repository map to give the model context beyond individual files.
- **Review changes with Git.** Inspect diffs, create commits, and undo AI-generated changes.
- **Iterate with checks.** Run linters and tests, then ask Patch to address failures.
- **Bring more context.** Add images, web pages, and voice input to your coding conversations.
- **Use your existing tools.** Work in the terminal alongside your editor, or try the experimental browser UI.

## Quick start

Requires **Python 3.10–3.14**. Install the `patch-code` package in a virtual environment:

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install patch-code
```

Open your project and start a conversation:

```bash
cd /path/to/your/project
python -m patch --model sonnet --api-key anthropic=YOUR_API_KEY
```

The `patch` command is also available when your virtual environment is active.
Use `python -m patch` to avoid ambiguity with the standard Unix `patch` utility.

Run `python -m patch --help` for all options. See the
[model configuration guide](patch/docs/models.md) for other providers.

### Install from source

To work with the current checkout instead of a published PyPI release:

```bash
git clone https://github.com/PierrunoYT/patch.git
cd patch
# Activate a virtual environment first, as shown above.
python -m pip install -e .
python -m patch --help
```

## Configuration

| Component | Name |
| --- | --- |
| PyPI package | `patch-code` |
| Python module | `patch` |
| Terminal command | `patch` or `python -m patch` |
| Configuration file | `.patch.conf.yml` |
| State and history files | `.patch*` |
| Application environment variables | `PATCH_*` |

Provider credentials keep their provider-specific names, such as `ANTHROPIC_API_KEY`
and `OPENAI_API_KEY`. Keep credentials out of version control.

A cloned repository writes its own `.patch.conf.yml` and `.env`, so Patch ignores
the settings in them that run commands, carry credentials, steer API traffic, or
write outside the repository. Use your own configuration for those, or
`--trust-repo-config` for a repository you have reviewed. See
[configuration options](patch/docs/config.md#repository-configuration-is-untrusted).

### Moving from Aider

Patch does not automatically read or migrate Aider configuration. Rename and review
your `.aider*` configuration files as `.patch*`, and update application environment
variables from `AIDER_*` to `PATCH_*` before using them with Patch.

## Documentation

- [Installation and optional extras](patch/docs/install.md)
- [Usage guide](patch/docs/usage.md)
- [Model configuration](patch/docs/models.md)
- [Configuration options](patch/docs/config.md)
- [Git integration](patch/docs/git.md)
- [Troubleshooting](patch/docs/troubleshooting.md)
- [Analytics](patch/docs/analytics.md)
- [Patch changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

These Markdown docs are packaged with Patch for `/help <question>`.
Patch does not maintain a separate documentation website.

## Logos

- [Wide PATCH wordmark](assets/logo.svg) — 2048 × 686, lettering only.
- [Square P icon](assets/logo-icon.svg) — 2048 × 2048.

Both SVGs use mint on charcoal and scale without requiring fonts.
The root `assets/` folder contains the logos.

## License and attribution

Patch is a fork of [Aider](https://github.com/Aider-AI/aider), developed in
[PierrunoYT/patch](https://github.com/PierrunoYT/patch). This repository is licensed
under [Apache 2.0](LICENSE.txt).

The [inherited release history](HISTORY.md) and retained [benchmark data](benchmark/data/)
are upstream material, not claims about Patch. Historical documentation links point
to upstream Aider's GitHub sources. The inherited website, articles, and recordings
are no longer bundled with Patch.
