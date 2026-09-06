# Troubleshooting

Start with `python -m patch --help` and `/help`. For installation/import problems
see [installation](install.md#installation-problems); for credentials and provider
errors see [models](models.md#api-keys). Report reproducible problems in
[Patch issues](https://github.com/PierrunoYT/patch/issues), omitting credentials,
private code, and unredacted logs.

## Edit errors

An edit error means Patch could not apply the model's requested format or match
its source text. Patch normally sends feedback to the model so it can retry.
If failures repeat, reduce the request, add the correct files, and use a model
with reliable editing support. Check [edit formats](models.md#edit-formats).
Review the diff: a failed response may still have applied some edits.

## Token limits

Use `/tokens` to inspect context usage. `/drop` unnecessary files and `/clear`
old chat history; ask for smaller changes. Large files, pasted output, and long
conversations consume input context. Output limits can truncate edits, so review
files and tests rather than assuming a finished response made complete changes.
Check [model metadata](models.md#model-warnings) if the reported limits look wrong.
