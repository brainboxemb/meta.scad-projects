#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .gitmodules ]]; then
    echo "ERROR: .gitmodules not found." >&2
    exit 1
fi

git config -f .gitmodules --get-regexp '^submodule\..*\.path$' |
while read -r key path; do
    name="${key#submodule.}"
    name="${name%.path}"
    url="$(git config -f .gitmodules --get "submodule.${name}.url")"

    if [[ -e "$path" ]]; then
        if [[ -e "$path/.git" ]]; then
            echo "Reusing existing Git checkout: $path"
            continue
        fi

        if [[ -n "$(find "$path" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" ]]; then
            echo "ERROR: cannot initialize $path because non-Git files already exist there." >&2
            exit 1
        fi
    fi

    if git ls-files --stage -- "$path" | grep -q '^160000 '; then
        echo "Initializing pinned submodule: $path"
        git submodule update --init -- "$path"
    else
        echo "Registering submodule: $path"
        git submodule add --force "$url" "$path"
    fi
done

git submodule sync
git submodule update --init

echo "SCAD ecosystem repositories are initialized."
