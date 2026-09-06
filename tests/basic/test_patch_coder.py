import os
import shutil
import tempfile
import unittest
from pathlib import Path

from patch.coders.patch_coder import PatchCoder
from patch.dump import dump  # noqa: F401
from patch.io import InputOutput
from patch.models import Model


def update_patch(path, move_to=None, old="one", new="two"):
    move = f"*** Move to: {move_to}\n" if move_to else ""

    return f"""*** Begin Patch
*** Update File: {path}
{move}@@
-{old}
+{new}
*** End Patch
"""


class TestPatchCoderMoves(unittest.TestCase):
    """A move writes its destination, so the destination needs authorizing."""

    def setUp(self):
        self.GPT35 = Model("gpt-3.5-turbo")

        self.original_cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp()
        # The project is a directory inside the temp dir, so ".." is somewhere
        # this test owns rather than the shared temp root.
        self.root = Path(self.tempdir) / "project"
        self.root.mkdir()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def make_coder(self, io, fnames=None, read_only_fnames=None):
        return PatchCoder(
            main_model=self.GPT35,
            io=io,
            fnames=fnames or [],
            read_only_fnames=read_only_fnames,
            use_git=False,
        )

    def test_move_inside_the_root_is_applied(self):
        source = Path("source.txt")
        source.write_text("one\n")

        coder = self.make_coder(InputOutput(yes=True), fnames=[str(source)])
        coder.partial_response_content = update_patch("source.txt", move_to="moved.txt")
        coder.apply_updates()

        self.assertFalse(source.exists())
        self.assertEqual(Path("moved.txt").read_text(), "two\n")

    def test_move_outside_the_root_is_refused(self):
        source = Path("source.txt")
        source.write_text("one\n")
        outside = Path(self.tempdir) / "moved.txt"

        coder = self.make_coder(InputOutput(yes=True), fnames=[str(source)])
        coder.partial_response_content = update_patch("source.txt", move_to="../moved.txt")
        coder.apply_updates()

        self.assertFalse(outside.exists())
        self.assertEqual(source.read_text(), "one\n")

    def test_move_onto_a_read_only_file_is_refused(self):
        source = Path("source.txt")
        source.write_text("one\n")
        protected = Path("protected.txt")
        protected.write_text("keep\n")

        coder = self.make_coder(
            InputOutput(yes=True),
            fnames=[str(source)],
            read_only_fnames=[str(protected.resolve())],
        )
        coder.partial_response_content = update_patch("source.txt", move_to="protected.txt")
        coder.apply_updates()

        self.assertEqual(protected.read_text(), "keep\n")
        self.assertEqual(source.read_text(), "one\n")

    def test_move_onto_an_existing_file_needs_explicit_approval(self):
        source = Path("source.txt")
        source.write_text("one\n")
        target = Path("target.txt")
        target.write_text("keep\n")

        # yes=True stands in for --yes-always, which must not approve an
        # overwrite on its own.
        coder = self.make_coder(InputOutput(yes=True), fnames=[str(source), str(target)])
        coder.partial_response_content = update_patch("source.txt", move_to="target.txt")
        coder.apply_updates()

        self.assertEqual(target.read_text(), "keep\n")
        self.assertEqual(source.read_text(), "one\n")

    def test_move_onto_an_existing_file_is_applied_when_approved(self):
        source = Path("source.txt")
        source.write_text("one\n")
        target = Path("target.txt")
        target.write_text("keep\n")

        io = InputOutput(yes=True)
        io.confirm_ask = lambda *args, **kwargs: True

        coder = self.make_coder(io, fnames=[str(source), str(target)])
        coder.partial_response_content = update_patch("source.txt", move_to="target.txt")
        coder.apply_updates()

        self.assertEqual(target.read_text(), "two\n")
        self.assertFalse(source.exists())


class TestPatchCoderSentinels(unittest.TestCase):
    """A patch without both sentinels may have been cut off."""

    def setUp(self):
        self.GPT35 = Model("gpt-3.5-turbo")

        self.original_cwd = os.getcwd()
        self.tempdir = tempfile.mkdtemp()
        os.chdir(self.tempdir)

        self.source = Path("source.txt")
        self.source.write_text("one\n")

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def make_coder(self):
        return PatchCoder(
            main_model=self.GPT35,
            io=InputOutput(yes=True),
            fnames=[str(self.source)],
            use_git=False,
        )

    def test_missing_end_sentinel_is_rejected(self):
        coder = self.make_coder()
        coder.partial_response_content = """*** Begin Patch
*** Update File: source.txt
@@
-one
+two
"""

        with self.assertRaises(ValueError):
            coder.get_edits()

        coder.apply_updates()

        self.assertEqual(self.source.read_text(), "one\n")
        self.assertIn("*** End Patch", coder.reflected_message)

    def test_missing_begin_sentinel_is_rejected(self):
        coder = self.make_coder()
        coder.partial_response_content = """*** Update File: source.txt
@@
-one
+two
*** End Patch
"""

        with self.assertRaises(ValueError):
            coder.get_edits()

        self.assertEqual(self.source.read_text(), "one\n")

    def test_content_that_is_not_a_patch_is_ignored(self):
        coder = self.make_coder()
        coder.partial_response_content = "I had a look, and everything seems fine.\n"

        self.assertEqual(coder.get_edits(), [])

    def test_prose_around_the_sentinels_is_allowed(self):
        coder = self.make_coder()
        coder.partial_response_content = f"""Here is the change:

{update_patch("source.txt")}
Let me know what you think.
"""
        coder.apply_updates()

        self.assertEqual(self.source.read_text(), "two\n")


if __name__ == "__main__":
    unittest.main()
