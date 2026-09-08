#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .gitmodules ]]; then
    echo "ERROR: .gitmodules not found." >&2
    exit 1
fi

git submodule sync
git submodule update --init

declare -a summary=()

while read -r key path; do
    name="${key#submodule.}"
    name="${name%.path}"

    if [[ ! -d "$path" ]]; then
        echo "ERROR: submodule path '$path' does not exist after initialization." >&2
        exit 1
    fi

    if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
        echo "ERROR: submodule '$path' has local changes." >&2
        echo "Commit, stash or discard them before updating." >&2
        exit 1
    fi

    old_commit="$(git -C "$path" rev-parse HEAD)"

    git -C "$path" fetch --prune origin

    remote_head="$(git -C "$path" symbolic-ref --quiet --short refs/remotes/origin/HEAD || true)"
    if [[ -z "$remote_head" ]]; then
        echo "ERROR: cannot determine origin default branch for '$path'." >&2
        exit 1
    fi

    branch="${remote_head#origin/}"

    if git -C "$path" show-ref --verify --quiet "refs/heads/$branch"; then
        git -C "$path" checkout "$branch"
    else
        git -C "$path" checkout -b "$branch" --track "origin/$branch"
    fi

    git -C "$path" pull --ff-only origin "$branch"

    new_commit="$(git -C "$path" rev-parse HEAD)"

    if [[ "$old_commit" == "$new_commit" ]]; then
        summary+=("$name|$branch|$old_commit|$new_commit|unchanged")
    else
        summary+=("$name|$branch|$old_commit|$new_commit|changed")
    fi
done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.path$')

echo
echo "Repository update summary"
echo "========================="

for row in "${summary[@]}"; do
    IFS='|' read -r name branch old_commit new_commit state <<< "$row"

    echo
    if [[ "$state" == "changed" ]]; then
        echo "$name"
        echo "  branch : $branch"
        echo "  old    : $old_commit"
        echo "  new    : $new_commit"
    else
        echo "$name - unchanged ($new_commit)"
    fi
done

echo
echo "Meta repository status:"
git status --short
echo
echo "Review the updated submodule pointers before committing them."
