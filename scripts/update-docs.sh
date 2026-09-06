#!/bin/bash

# exit when any command fails
set -e

if [ -z "$1" ]; then
  ARG=-r
else
  ARG=$1
fi

if [ "$ARG" != "--check" ]; then
  tail -1000 ~/.patch/analytics.jsonl > patch/website/assets/sample-analytics.jsonl
  cog -r patch/website/docs/faq.md
fi

# README.md before index.md, because index.md uses cog to include README.md
cog $ARG \
    README.md \
    patch/website/index.html \
    patch/website/HISTORY.md \
    patch/website/docs/usage/commands.md \
    patch/website/docs/languages.md \
    patch/website/docs/config/dotenv.md \
    patch/website/docs/config/options.md \
    patch/website/docs/config/patch_conf.md \
    patch/website/docs/config/adv-model-settings.md \
    patch/website/docs/config/model-aliases.md \
    patch/website/docs/leaderboards/index.md \
    patch/website/docs/leaderboards/edit.md \
    patch/website/docs/leaderboards/refactor.md \
    patch/website/docs/llms/other.md \
    patch/website/docs/more/infinite-output.md \
    patch/website/docs/legal/privacy.md
