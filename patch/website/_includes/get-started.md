
If you already have python 3.8-3.13 installed, you can get started quickly like this.

First, install patch:

{% include install.md %}

Start working with patch on your codebase:

```bash
# Change directory into your codebase
cd /to/your/project

# DeepSeek
patch --model deepseek --api-key deepseek=<key>

# Claude 3.7 Sonnet
patch --model sonnet --api-key anthropic=<key>

# o3-mini
patch --model o3-mini --api-key openai=<key>
```
