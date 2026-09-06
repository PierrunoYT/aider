import unittest
from pathlib import Path

from patch.coders import Coder
from patch.coders.udiff_coder import find_diffs
from patch.dump import dump  # noqa: F401
from patch.io import InputOutput
from patch.models import Model
from patch.utils import ChdirTemporaryDirectory


class TestUnifiedDiffCoder(unittest.TestCase):
    def test_find_diffs_single_hunk(self):
        # Test find_diffs with a single hunk
        content = """
Some text...

```diff
--- file.txt
+++ file.txt
@@ ... @@
-Original
+Modified
```
"""
        edits = find_diffs(content)
        dump(edits)
        self.assertEqual(len(edits), 1)

        edit = edits[0]
        self.assertEqual(edit[0], "file.txt")
        self.assertEqual(edit[1], ["-Original\n", "+Modified\n"])

    def test_find_diffs_dev_null(self):
        # Test find_diffs with a single hunk
        content = """
Some text...

```diff
--- /dev/null
+++ file.txt
@@ ... @@
-Original
+Modified
```
"""
        edits = find_diffs(content)
        dump(edits)
        self.assertEqual(len(edits), 1)

        edit = edits[0]
        self.assertEqual(edit[0], "file.txt")
        self.assertEqual(edit[1], ["-Original\n", "+Modified\n"])

    def test_find_diffs_dirname_with_spaces(self):
        # Test find_diffs with a single hunk
        content = """
Some text...

```diff
--- dir name with spaces/file.txt
+++ dir name with spaces/file.txt
@@ ... @@
-Original
+Modified
```
"""
        edits = find_diffs(content)
        dump(edits)
        self.assertEqual(len(edits), 1)

        edit = edits[0]
        self.assertEqual(edit[0], "dir name with spaces/file.txt")
        self.assertEqual(edit[1], ["-Original\n", "+Modified\n"])

    def test_find_multi_diffs(self):
        content = """
To implement the `--check-update` option, I will make the following changes:

1. Add the `--check-update` argument to the argument parser in `patch/main.py`.
2. Modify the `check_version` function in `patch/versioncheck.py` to return a boolean indicating whether an update is available.
3. Use the returned value from `check_version` in `patch/main.py` to set the exit status code when `--check-update` is used.

Here are the diffs for those changes:

```diff
--- patch/versioncheck.py
+++ patch/versioncheck.py
@@ ... @@
     except Exception as err:
         print_cmd(f"Error checking pypi for new version: {err}")
+        return False

--- patch/main.py
+++ patch/main.py
@@ ... @@
     other_group.add_argument(
         "--version",
         action="version",
         version=f"%(prog)s {__version__}",
         help="Show the version number and exit",
     )
+    other_group.add_argument(
+        "--check-update",
+        action="store_true",
+        help="Check for updates and return status in the exit code",
+        default=False,
+    )
     other_group.add_argument(
         "--apply",
         metavar="FILE",
```

These changes will add the `--check-update` option to the command-line interface and use the `check_version` function to determine if an update is available, exiting with status code `0` if no update is available and `1` if an update is available.
"""  # noqa: E501

        edits = find_diffs(content)
        dump(edits)
        self.assertEqual(len(edits), 2)
        self.assertEqual(len(edits[0][1]), 3)


class TestUnifiedDiffDryRun(unittest.TestCase):
    """A dry run answers what would happen, it does not touch the filesystem."""

    def setUp(self):
        self.GPT35 = Model("gpt-3.5-turbo")

    new_file_response = """```diff
--- /dev/null
+++ new.txt
@@ ... @@
+hello
```
"""

    def make_coder(self, dry_run):
        return Coder.create(
            self.GPT35,
            "udiff",
            io=InputOutput(dry_run=dry_run, yes=True),
            fnames=[],
            dry_run=dry_run,
            use_git=False,
        )

    def test_dry_run_creates_no_new_file(self):
        with ChdirTemporaryDirectory():
            coder = self.make_coder(dry_run=True)
            coder.partial_response_content = self.new_file_response
            coder.apply_updates()

            self.assertFalse(Path("new.txt").exists())

    def test_new_file_is_still_created_without_dry_run(self):
        with ChdirTemporaryDirectory():
            coder = self.make_coder(dry_run=False)
            coder.partial_response_content = self.new_file_response
            coder.apply_updates()

            self.assertEqual(Path("new.txt").read_text(), "hello\n")


if __name__ == "__main__":
    unittest.main()
