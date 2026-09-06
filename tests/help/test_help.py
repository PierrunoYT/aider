from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from patch import __version__, urls
from patch.commands import Commands, SwitchCoder
from patch.help import Help, fname_to_url, get_index, get_package_files


def test_package_files():
    files = list(get_package_files())
    assert {file.name for file in files} == {
        "usage.md",
        "install.md",
        "config.md",
        "models.md",
        "git.md",
        "troubleshooting.md",
        "analytics.md",
    }
    for file in files:
        text = file.read_text(encoding="utf-8")
        assert text.startswith("# ")
        assert "{%" not in text
        assert "{{" not in text


@pytest.mark.parametrize(
    "filename",
    [
        "usage.md",
        "patch/docs/usage.md",
        "/home/user/patch/docs/usage.md",
        r"C:\Users\user\patch\docs\usage.md",
    ],
)
def test_fname_to_url(filename):
    assert fname_to_url(filename) == urls.docs + "usage.md"


@pytest.mark.parametrize("filename", ["", "missing.md", "__init__.py", "usage.html"])
def test_fname_to_url_unknown(filename):
    assert fname_to_url(filename) == ""


def test_index_build_and_cache(tmp_path):
    core = MagicMock()
    parser = MagicMock()
    parser.MarkdownNodeParser.return_value.get_nodes_from_documents.side_effect = lambda docs: docs
    modules = {"llama_index.core": core, "llama_index.core.node_parser": parser}
    legacy_cache = tmp_path / ".patch" / "caches" / ("help." + __version__)
    legacy_cache.mkdir(parents=True)
    with patch.dict("sys.modules", modules), patch.object(Path, "home", return_value=tmp_path):
        index = get_index()
        core.load_index_from_storage.assert_not_called()
        assert core.Document.call_count == len(list(get_package_files()))
        for call in core.Document.call_args_list:
            metadata = call.kwargs["metadata"]
            resource = next(f for f in get_package_files() if f.name == metadata["filename"])
            assert call.kwargs["text"] == resource.read_text(encoding="utf-8")
            assert metadata["url"] == fname_to_url(resource.name)
        cache = tmp_path / ".patch" / "caches" / ("help.docs." + __version__)
        index.storage_context.persist.assert_called_once_with(cache)
        cache.mkdir()
        assert get_index() == core.load_index_from_storage.return_value
        core.StorageContext.from_defaults.assert_called_once_with(persist_dir=cache)
        assert core.VectorStoreIndex.call_count == 1


def test_help_initialization():
    core = MagicMock()
    embeddings = MagicMock()
    with (
        patch.dict(
            "sys.modules",
            {
                "llama_index.core": core,
                "llama_index.embeddings.huggingface": embeddings,
            },
        ),
        patch("patch.help.get_index") as get_index_mock,
    ):
        help_instance = Help()
    embeddings.HuggingFaceEmbedding.assert_called_once_with(model_name="BAAI/bge-small-en-v1.5")
    get_index_mock.return_value.as_retriever.assert_called_once_with(similarity_top_k=20)
    assert help_instance.retriever == get_index_mock.return_value.as_retriever.return_value


def test_ask():
    help_instance = Help.__new__(Help)
    help_instance.retriever = MagicMock()
    help_instance.retriever.retrieve.return_value = [
        SimpleNamespace(text="Use /add for editable files.", metadata={"url": urls.add_all_files}),
        SimpleNamespace(text="Additional context.", metadata={}),
    ]
    result = help_instance.ask("How do I add files?")
    help_instance.retriever.retrieve.assert_called_once_with("How do I add files?")
    assert "# Question: How do I add files?" in result
    assert f'<doc from_url="{urls.add_all_files}">\nUse /add for editable files.\n</doc>' in result
    assert "<doc>\nAdditional context.\n</doc>" in result


def test_help_command():
    coder = MagicMock()
    commands = Commands(MagicMock(), coder)
    with (
        patch("patch.commands.install_help_extra", return_value=True) as install,
        patch("patch.commands.Help") as help_class,
        patch("patch.coders.base_coder.Coder.create") as create,
    ):
        commands.cmd_help("")
        install.assert_not_called()
        help_class.return_value.ask.return_value = "Packaged documentation"
        for _ in range(2):
            with pytest.raises(SwitchCoder):
                commands.cmd_help("How do I use Patch?")
        install.assert_called_once()
        help_class.assert_called_once()
        assert create.return_value.run.call_count == 2
        assert create.return_value.run.call_args.args[0].startswith("Packaged documentation")
