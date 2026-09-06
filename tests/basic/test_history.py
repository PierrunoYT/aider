from unittest import TestCase, mock

from patch.history import ChatSummary
from patch.models import Model


def count(msg):
    if isinstance(msg, list):
        return sum(count(m) for m in msg)
    return len(msg["content"].split())


class TestChatSummary(TestCase):
    def setUp(self):
        self.mock_model = mock.Mock(spec=Model)
        self.mock_model.name = "gpt-3.5-turbo"
        self.mock_model.token_count = count
        self.mock_model.info = {"max_input_tokens": 4096}
        self.mock_model.simple_send_with_retries = mock.Mock()
        self.chat_summary = ChatSummary(self.mock_model, max_tokens=100)

    def test_initialization(self):
        self.assertIsInstance(self.chat_summary, ChatSummary)
        self.assertEqual(self.chat_summary.max_tokens, 100)

    def test_too_big(self):
        messages = [
            {"role": "user", "content": "This is a short message"},
            {"role": "assistant", "content": "This is also a short message"},
        ]
        self.assertFalse(self.chat_summary.too_big(messages))

        long_message = {"role": "user", "content": " ".join(["word"] * 101)}
        self.assertTrue(self.chat_summary.too_big([long_message]))

    def test_tokenize(self):
        messages = [
            {"role": "user", "content": "Hello world"},
            {"role": "assistant", "content": "Hi there"},
        ]
        tokenized = self.chat_summary.tokenize(messages)
        self.assertEqual(tokenized, [(2, messages[0]), (2, messages[1])])

    def test_summarize_all(self):
        self.mock_model.simple_send_with_retries.return_value = "This is a summary"
        messages = [
            {"role": "user", "content": "Hello world"},
            {"role": "assistant", "content": "Hi there"},
        ]
        summary = self.chat_summary.summarize_all(messages)
        self.assertEqual(
            summary,
            [
                {
                    "role": "user",
                    "content": (
                        "I spoke to you previously about a number of things.\nThis is a summary"
                    ),
                }
            ],
        )

    def test_summarize(self):
        N = 100
        messages = [None] * (2 * N)
        for i in range(N):
            messages[2 * i] = {"role": "user", "content": f"Message {i}"}
            messages[2 * i + 1] = {"role": "assistant", "content": f"Response {i}"}

        with mock.patch.object(
            self.chat_summary,
            "summarize_all",
            return_value=[{"role": "user", "content": "Summary"}],
        ):
            result = self.chat_summary.summarize(messages)

        print(result)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertLess(len(result), len(messages))
        self.assertEqual(result[0]["content"], "Summary")

    def test_fallback_to_second_model(self):
        mock_model1 = mock.Mock(spec=Model)
        mock_model1.name = "gpt-4"
        mock_model1.simple_send_with_retries = mock.Mock(side_effect=Exception("Model 1 failed"))
        mock_model1.info = {"max_input_tokens": 4096}
        mock_model1.token_count = lambda msg: len(msg["content"].split())

        mock_model2 = mock.Mock(spec=Model)
        mock_model2.name = "gpt-3.5-turbo"
        mock_model2.simple_send_with_retries = mock.Mock(return_value="Summary from Model 2")
        mock_model2.info = {"max_input_tokens": 4096}
        mock_model2.token_count = lambda msg: len(msg["content"].split())

        chat_summary = ChatSummary([mock_model1, mock_model2], max_tokens=100)

        messages = [
            {"role": "user", "content": "Hello world"},
            {"role": "assistant", "content": "Hi there"},
        ]

        summary = chat_summary.summarize_all(messages)

        # Check that both models were tried
        mock_model1.simple_send_with_retries.assert_called_once()
        mock_model2.simple_send_with_retries.assert_called_once()

        # Check that we got a summary from the second model
        self.assertEqual(
            summary,
            [
                {
                    "role": "user",
                    "content": (
                        "I spoke to you previously about a number of things.\nSummary from Model 2"
                    ),
                }
            ],
        )


class TestSummarizationConservesMessages(TestCase):
    """Every message is summarized or kept, never quietly dropped."""

    def setUp(self):
        self.summarized = []

        def send(messages):
            # Remember what the summarizer was given
            self.summarized.append(messages[-1]["content"])
            return "a summary"

        self.mock_model = mock.Mock(spec=Model)
        self.mock_model.name = "gpt-3.5-turbo"
        self.mock_model.token_count = count
        self.mock_model.info = {"max_input_tokens": 4096}
        self.mock_model.simple_send_with_retries = mock.Mock(side_effect=send)

    def history(self, num_messages):
        messages = []
        for i in range(num_messages):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": f"id{i} " + " ".join(["word"] * 20)})

        return messages

    def summarize(self, messages, max_tokens=100, max_input_tokens=4096):
        self.mock_model.info = {"max_input_tokens": max_input_tokens}
        summary = ChatSummary(self.mock_model, max_tokens=max_tokens)

        return summary.summarize_real(messages)

    def seen_ids(self, result, num_messages):
        """Which messages reached a summarizer call or survived in the tail."""
        text = "\n".join(self.summarized) + "\n" + "\n".join(m["content"] for m in result)

        return {f"id{i}" for i in range(num_messages) if f"id{i} " in text}

    def test_every_message_is_summarized_or_kept(self):
        messages = self.history(12)

        result = self.summarize(messages)

        self.assertEqual(self.seen_ids(result, 12), {f"id{i}" for i in range(12)})

    def test_messages_that_do_not_fit_are_summarized_in_chunks(self):
        messages = self.history(12)

        # A tiny input budget, so the head cannot be summarized in one call
        result = self.summarize(messages, max_input_tokens=600)

        self.assertGreater(len(self.summarized), 1)
        self.assertEqual(self.seen_ids(result, 12), {f"id{i}" for i in range(12)})

    def test_the_head_is_summarized_in_order(self):
        messages = self.history(12)

        self.summarize(messages)

        first_call = self.summarized[0]
        positions = [first_call.index(f"id{i} ") for i in range(4) if f"id{i} " in first_call]
        self.assertEqual(positions, sorted(positions))

    def test_the_newest_head_messages_are_not_dropped(self):
        # Issue #1279: the head was cut from the front, so the messages closest
        # to the conversation were the ones lost
        messages = self.history(12)

        self.summarize(messages, max_input_tokens=600)

        self.assertIn("id9 ", "\n".join(self.summarized))
