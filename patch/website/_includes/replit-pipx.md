To use patch with pipx on replit, you can run these commands in the replit shell:

```bash
pip install pipx
pipx run patch-code ...normal patch args...
```

If you install patch with pipx on replit and try and run it as just `patch` it will crash with a missing `libstdc++.so.6` library.
