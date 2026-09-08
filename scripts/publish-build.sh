#!/usr/bin/env bash
set -euo pipefail

if [[ ! -d bld ]] || [[ -z "$(find bld -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
    echo "ERROR: bld is empty." >&2
    exit 1
fi

if [[ -z "${GITHUB_REPOSITORY:-}" ]]; then
    echo "ERROR: GITHUB_REPOSITORY is required." >&2
    exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

cp -a bld/. "$tmp/"

git -C "$tmp" init -q
git -C "$tmp" checkout --orphan snapshot
git -C "$tmp" config user.name "github-actions[bot]"
git -C "$tmp" config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git -C "$tmp" add .
git -C "$tmp" commit -q -m "Update generated repository status"
git -C "$tmp" remote add origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git -C "$tmp" push --force origin HEAD:build
