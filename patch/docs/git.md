# Git integration

Patch works best in a Git repository. By default it commits its edits with a
generated message and can commit pre-existing dirty changes before editing those
files. Review changes with `/diff` and normal Git commands.

`--no-auto-commits` disables automatic commits of model edits.
`--no-dirty-commits` disables the pre-edit commit of existing changes.
`--no-git` disables Git integration. `/commit` asks Patch to commit changes;
`/git <arguments>` runs Git directly.

## Undo

`/undo` reverts the last eligible Patch commit. It is not a general backup system;
check `git status` and `git diff` before destructive Git operations. Keep your own
commits and backups, especially when automatic commits are disabled.

## Attribution

Use `--attribute-author`, `--attribute-committer`, and the commit-message
attribution options shown by `python -m patch --help` to control Patch attribution.
Configure your own Git user name and email before working in a repository.
