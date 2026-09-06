# Analytics

Patch ships no analytics destination. No analytics events are sent and no opt-in
prompt appears unless you configure your own PostHog project. Upstream Aider's
project keys have been removed. Patch operates no analytics service.

## Your own telemetry

The inherited instrumentation can be enabled with both
`--analytics-posthog-project-api-key KEY` and `--analytics`. The first time,
Patch asks you to confirm. `--analytics-posthog-host HOST` selects a custom host.
`--no-analytics` disables collection for the session;
`python -m patch --analytics-disable` records a permanent opt-out.

Events include feature usage, public model names, token counts, error indicators,
system information, and a random UUID. Unknown model names are redacted.
Automatic exception capture is disabled. Review [the source](../analytics.py)
before enabling instrumentation for your own deployment.

## Local logs

```bash
python -m patch --analytics-log events.jsonl --no-analytics
```

This writes events locally without uploading them. Review logs before sharing
them and keep them out of version control. User-level analytics preferences and
the UUID are stored in `~/.patch/analytics.json`.
