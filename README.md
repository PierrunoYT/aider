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
[model configuration guide](patch/website/docs/llms.md) for other providers.

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

### Moving from Aider

Patch does not automatically read or migrate Aider configuration. Rename and review
your `.aider*` configuration files as `.patch*`, and update application environment
variables from `AIDER_*` to `PATCH_*` before using them with Patch.

## Documentation

- [Usage guide](patch/website/docs/usage.md)
- [Model configuration](patch/website/docs/llms.md)
- [Configuration options](patch/website/docs/config.md)
- [Troubleshooting](patch/website/docs/troubleshooting.md)
- [Patch changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

## Logos

- [Wide PATCH wordmark](assets/logo.svg) — 2048 × 686, lettering only.
- [Square P icon](assets/logo-icon.svg) — 2048 × 2048.

Both SVGs use mint on charcoal and scale without requiring fonts.
The root `assets/` folder contains the logos; keep the website copies in
`patch/website/assets/` in sync when updating them.

## License and attribution

Patch is a fork of [Aider](https://github.com/Aider-AI/aider), developed in
[PierrunoYT/patch](https://github.com/PierrunoYT/patch). This repository is licensed
under [Apache 2.0](LICENSE.txt).

The [inherited release history](HISTORY.md), historical benchmarks, articles, and
recordings are preserved as upstream material, not claims about Patch. Links to
`aider.chat` in the documentation refer to upstream resources; they are not a Patch website.
