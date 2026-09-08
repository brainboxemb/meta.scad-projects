#!/usr/bin/env python3
"""Generate a cross-repository SCAD ecosystem status report.

The report combines:
- the commit pinned by the meta repository;
- the latest commit on each repository's remote default branch;
- the most recently created Git tag;
- the latest completed GitHub Actions run.

The script uses Git for repository/tag data and the GitHub REST API only for
Actions status. It intentionally writes generated output below bld/.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "repositories.json"
BUILD = ROOT / "bld"
REPORT = BUILD / "repository-status.md"
MERMAID = BUILD / "repository-status.mmd"


@dataclass
class RepoStatus:
    name: str
    role: str
    url: str
    path: Path
    pinned: str
    default_branch: str
    latest: str
    latest_tag: str
    sync: str
    actions: str
    actions_url: str | None
    last_commit_date: str


def run_git(*args: str, cwd: Path = ROOT, check: bool = True) -> str:
    """Run Git and return stripped stdout."""

    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed in {cwd}:\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def short(sha: str) -> str:
    return sha[:8] if sha else "-"


def pinned_commit(path: str) -> str:
    """Read the gitlink recorded by the current meta-repository commit."""

    row = run_git("ls-tree", "HEAD", "--", path)
    if not row:
        return ""
    fields = row.split()
    if len(fields) >= 3 and fields[0] == "160000":
        return fields[2]
    return ""


def prepare_submodule(path: Path) -> tuple[str, str, str]:
    """Fetch one submodule and return default branch, latest SHA and tag."""

    if not path.exists():
        raise RuntimeError(f"Submodule checkout missing: {path}")

    if run_git("status", "--porcelain", cwd=path):
        raise RuntimeError(f"Submodule has local changes: {path}")

    run_git("fetch", "--prune", "--tags", "origin", cwd=path)

    remote_head = run_git(
        "symbolic-ref",
        "--quiet",
        "--short",
        "refs/remotes/origin/HEAD",
        cwd=path,
        check=False,
    )
    if not remote_head:
        # Fresh/minimal clones occasionally do not carry origin/HEAD yet.
        branch = run_git(
            "remote",
            "show",
            "origin",
            cwd=path,
        )
        for line in branch.splitlines():
            if "HEAD branch:" in line:
                default_branch = line.split(":", 1)[1].strip()
                break
        else:
            raise RuntimeError(f"Cannot determine default branch for {path}")
    else:
        default_branch = remote_head.removeprefix("origin/")

    latest = run_git(
        "rev-parse",
        f"refs/remotes/origin/{default_branch}",
        cwd=path,
    )

    # Creator date works for annotated and lightweight tags and is more useful
    # here than lexical/semantic sorting because tag formats differ by repo.
    latest_tag = run_git(
        "tag",
        "--sort=-creatordate",
        "--format=%(refname:short)",
        cwd=path,
        check=False,
    ).splitlines()
    tag = latest_tag[0] if latest_tag else "-"

    commit_date = run_git(
        "show",
        "-s",
        "--format=%cI",
        latest,
        cwd=path,
    )

    return default_branch, latest, tag, commit_date


def github_actions_status(repository_url: str) -> tuple[str, str | None]:
    """Return the latest completed Actions conclusion for a public repo."""

    slug = repository_url.rstrip("/").split("github.com/", 1)[1]
    api = (
        f"https://api.github.com/repos/{slug}/actions/runs"
        "?status=completed&per_page=1"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "meta.scad-projects",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(api, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        return f"unknown ({exc.__class__.__name__})", None

    runs = payload.get("workflow_runs", [])
    if not runs:
        return "no completed runs", None

    run = runs[0]
    conclusion = run.get("conclusion") or run.get("status") or "unknown"
    return conclusion, run.get("html_url")


def collect() -> list[RepoStatus]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    rows: list[RepoStatus] = []

    for repo in config["repositories"]:
        path = ROOT / repo["path"]
        pinned = pinned_commit(repo["path"])
        branch, latest, tag, commit_date = prepare_submodule(path)
        actions, actions_url = github_actions_status(repo["url"])

        if not pinned:
            sync = "no gitlink"
        elif pinned == latest:
            sync = "up to date"
        else:
            sync = "update available"

        rows.append(
            RepoStatus(
                name=repo["name"],
                role=repo["role"],
                url=repo["url"],
                path=path,
                pinned=pinned,
                default_branch=branch,
                latest=latest,
                latest_tag=tag,
                sync=sync,
                actions=actions,
                actions_url=actions_url,
                last_commit_date=commit_date,
            )
        )

    return rows


def markdown(rows: list[RepoStatus]) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# SCAD ecosystem repository status",
        "",
        f"Generated: **{generated}**",
        "",
        "This report compares the commits pinned by `meta.scad-projects` with",
        "the current default branches of the tracked repositories.",
        "",
        "| Repository | Role | Pinned | Default branch | Latest | Latest tag | Sync | Actions | Last commit |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        repo = f"[`{row.name}`]({row.url})"
        pinned = f"`{short(row.pinned)}`" if row.pinned else "-"
        latest = f"`{short(row.latest)}`"
        actions = row.actions
        if row.actions_url:
            actions = f"[{actions}]({row.actions_url})"

        lines.append(
            f"| {repo} | {row.role} | {pinned} | `{row.default_branch}` | "
            f"{latest} | `{row.latest_tag}` | **{row.sync}** | {actions} | "
            f"{row.last_commit_date} |"
        )

    lines += [
        "",
        "## Versioned architecture view",
        "",
        "```mermaid",
        mermaid_body(rows),
        "```",
        "",
        "### Relationship meaning",
        "",
        "- `template.scad-project -> tool.scad-project`: build tooling",
        "- `template.scad-project -> docker.scad-toolchain`: runtime",
        "- `template.scad-project -> lib.scad.clamps`: design / reusable CAD",
        "- `tool.scad-project -> docker.scad-toolchain`: runs on",
        "- `docker.scad-toolchain.test -.-> docker.scad-toolchain`: verifies",
        "",
        "The architecture itself is documented in `docs/architecture.md`; this",
        "page is the generated current-state view.",
        "",
    ]
    return "\n".join(lines)


def mermaid_label(row: RepoStatus) -> str:
    tag = row.latest_tag if row.latest_tag != "-" else "no tag"
    suffix = "✓" if row.sync == "up to date" else "↑ update"
    return f"{row.name}<br/>{tag}<br/>{suffix}"


def mermaid_body(rows: list[RepoStatus]) -> str:
    by_name = {row.name: row for row in rows}
    return "\n".join(
        [
            "flowchart TD",
            "",
            '    subgraph RUNTIME["Runtime / Build environment"]',
            f'        TOOLCHAIN["{mermaid_label(by_name["docker.scad-toolchain"])}"]',
            "    end",
            "",
            '    subgraph WORKFLOW["Project workflow"]',
            f'        TOOL["{mermaid_label(by_name["tool.scad-project"])}"]',
            "    end",
            "",
            '    subgraph DESIGN["Design / Consumers"]',
            f'        TEMPLATE["{mermaid_label(by_name["template.scad-project"])}"]',
            f'        CLAMPS["{mermaid_label(by_name["lib.scad.clamps"])}"]',
            "    end",
            "",
            '    subgraph VERIFY["Verification"]',
            f'        TEST["{mermaid_label(by_name["docker.scad-toolchain.test"])}"]',
            "    end",
            "",
            '    TEMPLATE -->|"build tooling"| TOOL',
            '    TEMPLATE -->|"runtime"| TOOLCHAIN',
            '    TEMPLATE -->|"design / reusable CAD"| CLAMPS',
            '    TOOL -->|"runs on"| TOOLCHAIN',
            '    TEST -.->|"verifies"| TOOLCHAIN',
        ]
    )


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    rows = collect()
    REPORT.write_text(markdown(rows), encoding="utf-8")
    MERMAID.write_text(mermaid_body(rows) + "\n", encoding="utf-8")

    print(f"Generated {REPORT.relative_to(ROOT)}")
    print(f"Generated {MERMAID.relative_to(ROOT)}")

    for row in rows:
        print(
            f"{row.name}: {row.sync}; tag={row.latest_tag}; "
            f"actions={row.actions}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
