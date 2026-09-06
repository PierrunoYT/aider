# Using Patch

Patch is an AI pair-programming tool for your terminal, forked from Aider.
Start in your project directory with `python -m patch file1.py file2.py`, then
describe the change you want. Review the edits and run your tests.
See [installation](install.md), [models](models.md), [configuration](config.md),
[Git integration](git.md), and [troubleshooting](troubleshooting.md).

## Adding files

Use `/add path/to/file` to share editable files, `/read path/to/file` for read-only
context, `/ls` to list files, and `/drop path/to/file` to remove files from chat.
Only add files needed for the task: adding everything costs tokens and can confuse
the model. The repository map supplies related context without adding every file.
Use `/tokens` to inspect context usage.

## Large repositories

Start Patch in the repository and add only the files you expect to edit.
Use `.patchignore` with Git-ignore patterns to exclude irrelevant files from the
repository map and file discovery. Adjust `--map-tokens` to control map size;
`--map-tokens 0` disables the map. `/map` shows it and `/map-refresh` refreshes it.

## Commands and modes

- `/help` lists commands without installing extras. `/help <question>` retrieves
  these packaged docs and asks your configured model for an answer; it requires
  the [help extra](install.md#interactive-help) and may incur model API charges.
- `/ask <question>` discusses code without editing; `/code <request>` requests edits.
- `/architect <request>` uses a planning model followed by an editor model.
  `/chat-mode` changes the mode for subsequent messages.
- `/model <name>` changes the main model; `/models <query>` searches model names.
- `/diff` reviews the last changes; `/undo` undoes the last eligible Patch commit.
- `/run <command>` runs a shell command and offers to add its output to chat.
- `/test <command>` runs tests and offers to fix failures; `/lint` runs configured linters.
- `/clear` clears chat history; `/reset` also drops files; `/exit` ends the session.

## More context

Use `/web <URL>` to read a page, `/add` for a supported image, and `/voice` for
microphone transcription. Voice requires an audio device and transcription provider
credentials. Use `/paste` for clipboard content and `/editor` to write a prompt
in your editor. `/multiline-mode` toggles multiline input.

`--watch-files` reacts to AI comment markers in source files. Only enable it in
trusted projects: other local processes that write files can trigger model turns.
The experimental `--browser` UI requires the [browser extra](install.md#browser-ui).
It binds to `127.0.0.1` and has no authentication, so only override
`PATCH_GUI_ADDRESS` on a network you trust.
