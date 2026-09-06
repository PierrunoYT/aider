---
parent: More info
nav_order: 500
description: Off by default; Patch collects nothing unless you configure a destination.
---

# Analytics

**Patch collects no analytics.** It ships no analytics destination of its own,
so there is nothing to opt out of: no events leave your machine, and you are
never prompted about analytics.

Patch is a fork of Aider. Upstream Aider collects opt-in analytics through a
PostHog project it operates, and Patch inherited that code. The upstream project
key has been removed, and the collection path is now inert unless you
deliberately point it at a PostHog project you control.

## Collecting analytics for yourself

The instrumentation is still in the source, so you can use it to observe your
own usage. Both of these are needed before anything is sent:

- `--analytics-posthog-project-api-key KEY` — the PostHog project to send to.
  Without it, analytics stay off no matter what else you pass.
- `--analytics` — enable collection for the session. The first time, Patch asks
  you to confirm.

`--analytics-posthog-host HOST` selects a self-hosted PostHog installation
instead of the default cloud host.

`--no-analytics` turns collection off for a session, and `patch
--analytics-disable` records a permanent opt-out that overrides everything
above.

## Logging events locally

You can write events to a local file without sending them anywhere. This works
whether or not a PostHog project is configured:

```
patch --analytics-log filename.jsonl --no-analytics
```

The log file is written on your machine and is never uploaded.

## What the instrumentation records

When you enable it against your own project, it records:

- which LLMs are used and with how many tokens,
- which of patch's edit formats are used,
- how often features and commands are used,
- information about exceptions and errors,
- etc

Events carry an anonymous, randomly generated UUID4 identifier. Your code, chat
messages, and API keys are never included, and model names that are not in the
public model database are redacted.

### Analytics code

Since patch is open source, every place it can record an event is visible in the
source. They can be viewed using
[GitHub search](https://github.com/search?q=repo%3APierrunoYT%2Fpatch+%22.event%28%22&type=code).

### Sample analytics data

To get a better sense of the shape of the data, you can review some
[sample analytics logs](https://github.com/PierrunoYT/patch/blob/main/patch/website/assets/sample-analytics.jsonl).
These are 1,000 events retained from upstream Aider, kept as an example of the
event format.

## Reporting issues

If you have concerns about the analytics code or our data practices, please open
a [GitHub Issue](https://github.com/PierrunoYT/patch/issues).

## Privacy policy

The [privacy policy](/docs/legal/privacy.html) retained on this site is upstream
Aider's and describes the aider.chat service. It does not describe Patch, which
operates no website and no analytics service.
