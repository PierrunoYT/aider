---
title: Installation
nav_order: 20
description: How to install Patch.
---

# Installation

Install Patch directly from PyPI:

```bash
python -m pip install patch-code
```

Then change to a project and start a conversation:

```bash
cd /path/to/your/project
python -m patch --model sonnet --api-key anthropic=<key>
```

The `patch` command is also available once the package is installed. Prefer
`python -m patch` to avoid ambiguity with the standard Unix `patch` utility.

Patch requires Python 3.10 through 3.14. A virtual environment or `pipx` can be
used to isolate its dependencies.

See the [usage guide](/docs/usage.html) and [LLM configuration guide](/docs/llms.html)
for next steps.
