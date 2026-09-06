import io as io_module
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest

from patch.main import get_gui_address, launch_gui, main


class FakeSessionState(dict):
    """Stand-in for st.session_state, which is per browser session."""

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class TestBrowser(unittest.TestCase):
    @pytest.mark.installer
    @patch("patch.main.launch_gui")
    def test_browser_flag_imports_streamlit(self, mock_launch_gui):
        os.environ["PATCH_ANALYTICS"] = "false"

        # Run main with --browser and --yes flags
        main(["--browser", "--yes"])

        # Check that launch_gui was called
        mock_launch_gui.assert_called_once()

        # Try to import streamlit
        try:
            import streamlit  # noqa: F401

            streamlit_imported = True
        except ImportError:
            streamlit_imported = False

        # Assert that streamlit was successfully imported
        self.assertTrue(
            streamlit_imported, "Streamlit should be importable after running with --browser flag"
        )


class TestGuiAddress(unittest.TestCase):
    """The GUI is unauthenticated, so it must not bind every interface."""

    def setUp(self):
        env = {k: v for k, v in os.environ.items()}
        env.pop("PATCH_GUI_ADDRESS", None)
        env.pop("STREAMLIT_SERVER_ADDRESS", None)
        patcher = patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def launch(self):
        with patch("patch.main.write_streamlit_credentials"):
            with patch("streamlit.web.cli.main") as mock_cli_main:
                out = io_module.StringIO()
                with redirect_stdout(out):
                    launch_gui([])

        st_args = mock_cli_main.call_args[0][0]
        return st_args, out.getvalue()

    def test_default_address_is_loopback(self):
        self.assertEqual(get_gui_address(), "127.0.0.1")

    def test_blank_env_var_is_ignored(self):
        os.environ["PATCH_GUI_ADDRESS"] = "  "
        self.assertEqual(get_gui_address(), "127.0.0.1")

    def test_env_vars_override_the_default(self):
        os.environ["STREAMLIT_SERVER_ADDRESS"] = "192.168.1.5"
        self.assertEqual(get_gui_address(), "192.168.1.5")

        os.environ["PATCH_GUI_ADDRESS"] = "0.0.0.0"
        self.assertEqual(get_gui_address(), "0.0.0.0")

    def test_launch_gui_binds_loopback_by_default(self):
        st_args, output = self.launch()

        self.assertIn("--server.address=127.0.0.1", st_args)
        self.assertEqual(
            [arg for arg in st_args if arg.startswith("--server.address=")],
            ["--server.address=127.0.0.1"],
        )
        self.assertNotIn("WARNING", output)

    def test_launch_gui_honors_address_override_and_warns(self):
        os.environ["PATCH_GUI_ADDRESS"] = "0.0.0.0"

        st_args, output = self.launch()

        self.assertIn("--server.address=0.0.0.0", st_args)
        self.assertIn("WARNING", output)

    def test_launch_gui_does_not_warn_about_localhost(self):
        os.environ["PATCH_GUI_ADDRESS"] = "localhost"

        st_args, output = self.launch()

        self.assertIn("--server.address=localhost", st_args)
        self.assertNotIn("WARNING", output)


class TestGuiSessionIsolation(unittest.TestCase):
    """Chat history, files and undo state must not be shared between sessions."""

    def test_state_instances_do_not_share_keys(self):
        from patch.gui import State

        one = State()
        other = State()

        one.init("messages", ["one"])
        self.assertTrue(other.init("messages", ["other"]))

        self.assertEqual(one.messages, ["one"])
        self.assertEqual(other.messages, ["other"])

    def test_capture_io_instances_do_not_share_lines(self):
        from patch.gui import CaptureIO

        one = CaptureIO(pretty=False, yes=True, fancy_input=False)
        other = CaptureIO(pretty=False, yes=True, fancy_input=False)

        one.tool_output("hello", log_only=False)

        self.assertEqual(other.get_captured_lines(), [])
        self.assertEqual(one.get_captured_lines(), ["hello"])

    def test_state_is_per_session(self):
        from patch import gui

        with patch.object(gui.st, "session_state", FakeSessionState()):
            first = gui.get_state()
            self.assertIs(gui.get_state(), first)

        with patch.object(gui.st, "session_state", FakeSessionState()):
            second = gui.get_state()

        self.assertIsNot(first, second)

    def test_coder_is_per_session(self):
        from patch import gui

        with patch.object(gui, "create_coder", side_effect=lambda: object()) as mock_create:
            with patch.object(gui.st, "session_state", FakeSessionState()):
                first = gui.get_coder()
                self.assertIs(gui.get_coder(), first)

            with patch.object(gui.st, "session_state", FakeSessionState()):
                second = gui.get_coder()

        self.assertIsNot(first, second)
        self.assertEqual(mock_create.call_count, 2)


if __name__ == "__main__":
    unittest.main()
