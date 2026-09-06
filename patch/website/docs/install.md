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

Then change to a project and run `patch`:

```bash
cd /path/to/your/project
patch --model sonnet --api-key anthropic=<key>
```

Patch requires Python 3.10 or later. A virtual environment or `pipx` can be used to
isolate its dependencies.

See the [usage guide](/docs/usage.html) and [LLM configuration guide](/docs/llms.html)
for next steps.
