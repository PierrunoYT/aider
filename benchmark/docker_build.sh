#!/bin/bash

set -e

docker build \
       --file benchmark/Dockerfile \
       -t patch-benchmark \
       .
