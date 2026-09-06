---
parent: More info
nav_order: 100
description: Patch is tightly integrated with git.
---

# Git integration

Patch works best with code that is part of a git repo.
Patch is tightly integrated with git, which makes it easy to:

  - Use the `/undo` command to instantly undo any AI changes that you don't like.
  - Go back in the git history to review the changes that patch made to your code
  - Manage a series of patch's changes on a git branch

Patch uses git in these ways:

- It asks to create a git repo if you launch it in a directory without one.
- Whenever patch edits a file, it commits those changes with a descriptive commit message. This makes it easy to undo or review patch's changes. 
- Patch takes special care before editing files that already have uncommitted changes (dirty files). Patch will first commit any preexisting changes with a descriptive commit message. 
This keeps your edits separate from patch's edits, and makes sure you never lose your work if patch makes an inappropriate change.

## In-chat commands

Patch also allows you to use 
[in-chat commands](/docs/usage/commands.html)
to perform git operations:

- `/diff` will show all the file changes since the last message you sent.
- `/undo` will undo and discard the last change.
- `/commit` to commit all dirty changes with a sensible commit message.
- `/git` will let you run raw git commands to do more complex management of your git history.

You can also manage your git history outside of patch with your preferred git tools.

## Disabling git integration

While it is not recommended, you can disable patch's use of git in a few ways:

  - `--no-auto-commits` will stop patch from git committing each of its changes.
  - `--no-dirty-commits` will stop patch from committing dirty files before applying its edits.
  - `--no-git` will completely stop patch from using git on your files. You should ensure you are keeping sensible backups of the files you are working with.
  - `--git-commit-verify` will run pre-commit hooks when making git commits. By default, patch skips pre-commit hooks by using the `--no-verify` flag (`--git-commit-verify=False`).

## Commit messages

Patch sends the `--weak-model` a copy of the diffs and the chat history
and asks it to produce a commit message.
By default, patch creates commit messages which follow
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

You can customize the
[commit prompt](https://github.com/PierrunoYT/patch/blob/main/patch/prompts.py#L5)
with the `--commit-prompt` option.
You can place that on the command line, or 
[configure it via a config file or environment variables](https://aider.chat/docs/config.html).


## Commit attribution

Patch marks commits that it either authored or committed.

- If patch authored the changes in a commit, they will have "(patch)" appended to the git author and git committer name metadata.
- If patch simply committed changes (found in dirty files), the commit will have "(patch)" appended to the git committer name metadata.

You can use `--no-attribute-author` and `--no-attribute-committer` to disable
modification of the git author and committer name fields.

Additionally, you can use the following options to prefix commit messages:

- `--attribute-commit-message-author`: Prefix commit messages with 'patch: ' if patch authored the changes.
- `--attribute-commit-message-committer`: Prefix all commit messages with 'patch: ', regardless of whether patch authored the changes or not.

Finally, you can use `--attribute-co-authored-by` to have patch append a Co-authored-by trailer to the end of the commit string. 
This will disable appending `(patch)` to the git author and git committer unless you have explicitly enabled those settings.

