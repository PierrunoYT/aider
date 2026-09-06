# Installing Patch

Patch supports Python 3.10–3.14. Use an isolated virtual environment:

```bash
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install patch-code
python -m patch --help
```

Run `python -m pip install --upgrade patch-code` to upgrade. Update notices do not
install anything automatically. Use `python -m patch` to avoid the Unix `patch`
utility. For source development see [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Interactive help

```bash
python -m pip install 'patch-code[help]' --extra-index-url https://download.pytorch.org/whl/cpu
```

`/help <question>` can offer to install this extra. The first use downloads a
Hugging Face embedding model and indexes the packaged Markdown docs; subsequent
uses cache the index under `~/.patch/caches/`. Retrieval runs locally, but the
question and relevant docs are sent to your configured chat model for an answer.
Bare `/help` and `python -m patch --help` do not require this extra.

## Browser UI

```bash
python -m pip install 'patch-code[browser]'
python -m patch --browser
```

The experimental UI is intended for a trusted single user. Do not expose it to
untrusted networks or share it with other users: it can edit files and run commands.

## Enable Playwright

For pages that need browser rendering:

```bash
python -m pip install 'patch-code[playwright]'
python -m playwright install --with-deps chromium
```

## Installation problems

Check that `python --version` is supported and `python -m pip --version` points at
the active environment. Use the same Python for installation and launch. Avoid
naming local files `patch.py` or `patch`, which can shadow the installed package.
Recreate the virtual environment if it contains incompatible dependencies.
