#!/bin/bash

# exit when any command fails
set -e

# Add verbosity flag to see more details about dependency resolution
VERBOSITY="-v"  # Use -v for less detail, -vvv for even more detail

# Preserve Python and platform markers instead of locking only the host interpreter.
RESOLUTION=(--universal --python-version 3.10)

# First compile the common constraints of the full requirement suite
# to make sure that all versions are mutually consistent across files
uv pip compile \
    $VERBOSITY \
    "${RESOLUTION[@]}" \
    --no-strip-extras \
    --output-file=requirements/common-constraints.txt \
    requirements/requirements.in \
    requirements/requirements-*.in \
    "$@"

# Compile the base requirements
uv pip compile \
    $VERBOSITY \
    "${RESOLUTION[@]}" \
    --no-strip-extras \
    --constraint=requirements/common-constraints.txt \
    --output-file=requirements.txt \
    requirements/requirements.in \
    "$@"

# Compile additional requirements files
SUFFIXES=(dev help browser playwright)

for SUFFIX in "${SUFFIXES[@]}"; do
    uv pip compile \
        $VERBOSITY \
        "${RESOLUTION[@]}" \
        --no-strip-extras \
        --constraint=requirements/common-constraints.txt \
        --output-file=requirements/requirements-${SUFFIX}.txt \
        requirements/requirements-${SUFFIX}.in \
        "$@"
done
