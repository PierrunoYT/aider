import argparse
import unittest

from patch.dump import dump  # noqa: F401
from patch.format_settings import format_settings, mask_setting, scrub_sensitive_info


class FakeParser:
    """Stands in for the configargparse parser's own settings output."""

    def __init__(self, values=""):
        self.values = values

    def format_values(self):
        return self.values


def make_args(**kwargs):
    args = argparse.Namespace(
        openai_api_key=None,
        anthropic_api_key=None,
        api_key=[],
        set_env=[],
    )
    for name, value in kwargs.items():
        setattr(args, name, value)

    return args


class TestScrubSensitiveInfo(unittest.TestCase):
    """Credentials must not reach the terminal or the chat history file."""

    def scrub(self, text, **kwargs):
        return scrub_sensitive_info(make_args(**kwargs), text)

    def test_masks_the_dedicated_key_arguments(self):
        text = "--openai-api-key sk-openai-secret --anthropic-api-key sk-ant-secret"

        scrubbed = self.scrub(
            text,
            openai_api_key="sk-openai-secret",
            anthropic_api_key="sk-ant-secret",
        )

        self.assertNotIn("sk-openai-secret", scrubbed)
        self.assertNotIn("sk-ant-secret", scrubbed)
        self.assertIn("...cret", scrubbed)

    def test_masks_the_value_of_a_provider_key(self):
        text = "python -m patch --api-key deepseek=ds-secret-value"

        scrubbed = self.scrub(text, api_key=["deepseek=ds-secret-value"])

        self.assertNotIn("ds-secret-value", scrubbed)
        self.assertIn("deepseek=", scrubbed)

    def test_masks_a_secret_set_env_value(self):
        text = "python -m patch --set-env MY_TOKEN=abc"

        scrubbed = self.scrub(text, set_env=["MY_TOKEN=abc"])

        self.assertNotIn("=abc", scrubbed)

    def test_masks_a_long_set_env_value(self):
        text = "python -m patch --set-env SOMETHING=super-secret-value"

        scrubbed = self.scrub(text, set_env=["SOMETHING=super-secret-value"])

        self.assertNotIn("super-secret-value", scrubbed)

    def test_leaves_ordinary_short_values_alone(self):
        text = "python -m patch --set-env DEBUG=1 --map-tokens 1024"

        scrubbed = self.scrub(text, set_env=["DEBUG=1"])

        self.assertEqual(scrubbed, text)

    def test_masks_any_secret_looking_argument(self):
        text = "posthog key: ph-project-secret"

        scrubbed = self.scrub(text, analytics_posthog_project_api_key="ph-project-secret")

        self.assertNotIn("ph-project-secret", scrubbed)


class TestMaskSetting(unittest.TestCase):
    def test_masks_the_value_side(self):
        self.assertEqual(mask_setting("deepseek=abcdefgh"), "deepseek=...efgh")

    def test_short_values_become_ellipsis(self):
        self.assertEqual(mask_setting("DEBUG=1"), "DEBUG=...")

    def test_leaves_a_plain_value_alone(self):
        self.assertEqual(mask_setting("no-pair-here"), "no-pair-here")


class TestFormatSettings(unittest.TestCase):
    def test_settings_output_masks_every_pair(self):
        args = make_args(
            api_key=["deepseek=ds-secret-value"],
            set_env=["DEBUG=1", "MY_TOKEN=another-secret"],
            openai_api_key="sk-openai-secret",
        )
        parser = FakeParser("--api-key: ['deepseek=ds-secret-value']\n")

        settings = format_settings(parser, args)

        self.assertNotIn("ds-secret-value", settings)
        self.assertNotIn("another-secret", settings)
        self.assertNotIn("sk-openai-secret", settings)
        self.assertIn("DEBUG=...", settings)


if __name__ == "__main__":
    unittest.main()
