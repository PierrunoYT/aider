# Troubleshooting

Start with `python -m patch --help` and `/help`. For installation/import problems
see [installation](install.md#installation-problems); for credentials and provider
errors see [models](models.md#api-keys). Report reproducible problems in
[Patch issues](https://github.com/PierrunoYT/patch/issues), omitting credentials,
private code, and unredacted logs.

## A setting from the repository is ignored

Patch reports `Ignoring ... which the repository supplies` when a checkout's own
`.patch.conf.yml` or `.env` sets something that runs commands, carries
credentials, steers API traffic, or writes outside the repository. Move the
setting to `~/.patch.conf.yml`, `~/.env`, a `--config` or `--env-file` you name,
or the command line. To honor a repository you have reviewed, run it with
`--trust-repo-config`. The same applies to a repository's
`.patch.model.settings.yml`. See
[repository configuration is untrusted](config.md#repository-configuration-is-untrusted).

## The browser UI is not reachable from another machine

`--browser` listens on `127.0.0.1` because the UI has no authentication and can
edit the repository. `PATCH_GUI_ADDRESS` changes the address; only use it on a
network you trust. Each browser session keeps its own chat history and files, so
reloading the page starts a new session.

## Edit errors

An edit error means Patch could not apply the model's requested format or match
its source text. Patch normally sends feedback to the model so it can retry.
A response that stops mid-listing, because the model hit its output limit or the
connection was cut, is rejected rather than applied: an unterminated ``` block in
the `whole` format would otherwise replace a file with the part that arrived.
If failures repeat, reduce the request, add the correct files, and use a model
with reliable editing support. Check [edit formats](models.md#edit-formats).
Review the diff: a failed response may still have applied some edits.

## Token limits

Use `/tokens` to inspect context usage. `/drop` unnecessary files and `/clear`
old chat history; ask for smaller changes. Large files, pasted output, and long
conversations consume input context. Output limits can truncate edits, so review
files and tests rather than assuming a finished response made complete changes.
Check [model metadata](models.md#model-warnings) if the reported limits look wrong.
