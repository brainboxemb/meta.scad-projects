# Versioning and compatibility

## Independent repository versions

Each repository is independently versioned.

Matching version numbers across repositories do not imply a coordinated
release set.

Current ecosystem examples include:

```text
docker.scad-toolchain        independent runtime releases
tool.scad-project            v0.4.4 dependency/update architecture
template.scad-project        independent consumer history
lib.scad.clamps              independent library history
```

A ZIP/snapshot filename used during development is not automatically an
official Git release tag. Only tags actually created in the owning repository
are releases for dependency-resolution purposes.

## Dependency policy versus dependency lock

Consumer repositories declare dependency intent in `project.yml`.

Example:

```yaml
tooling:
  tool_scad_project:
    type: git-submodule
    url: https://github.com/brainboxemb/tool.scad-project.git
    path: tools/tool.scad-project
    ref: v0.4.4

externals:
  - name: lib.scad.clamps
    type: git-submodule
    url: https://github.com/brainboxemb/lib.scad.clamps.git
    path: dsg/openscad/ext/lib.scad.clamps
    ref: main
```

The `ref` is policy. The parent repository's Git tree stores the exact
dependency commit as a submodule gitlink.

Therefore:

```text
project.yml ref
    what should be resolved when intentionally updating

gitlink commit
    what a normal clone/build must use
```

This preserves reproducibility even for a floating policy such as `main`.

## Supported refs

### Exact tag

```yaml
ref: v0.4.4
```

Resolve the exact tag.

Use this for stable/reproducible tooling and library releases.

### Latest stable release

```yaml
ref: latest
```

Resolve the highest stable semantic-version tag matching `vX.Y.Z` / `X.Y.Z`.

`latest` does not mean the default branch and must not fall back to it if no
stable release tag exists.

### Explicit branch

```yaml
ref: main
```

Resolve the current remote branch head when intentionally running
`update-repo`.

This is useful for integration testing against unreleased development.

## Update semantics

Consumer repositories use three distinct operations:

```text
bootstrap
    establish/repair submodule registrations and restore committed gitlinks

repo-sync
    restore the exact commits already locked in the parent repository

update-repo
    intentionally resolve project.yml refs and update gitlinks
```

`update-repo` never commits automatically.

The canonical root `bootstrap.*` and `update-repo.*` scripts from
`tool.scad-project` are Python-free.

For the tooling dependency, `update-repo` additionally aligns literal reusable
GitHub Actions refs with the resolved tooling ref because GitHub Actions does
not allow that `uses:` ref to be dynamically interpolated from `project.yml`.

## Current reference-consumer policies

At the time this architecture was introduced:

| Consumer | Dependency | Configured policy |
| --- | --- | --- |
| `template.scad-project` | `tool.scad-project` | `v0.4.4` |
| `template.scad-project` | `lib.scad.clamps` | `main` |
| `lib.scad.clamps` | `tool.scad-project` | `v0.4.4` |

The template follows `lib.scad.clamps/main` because the library does not yet
have an established stable release-tag series. This should not be represented
as `latest`, because `latest` has a precise release-oriented meaning.

## Compatibility map

The meta repository should describe tested combinations, not infer
compatibility merely from matching version numbers.

A future generated compatibility report could combine:

- consumer `project.yml` policies;
- resolved gitlinks;
- toolchain image refs;
- completed CI/integration results.

Until such checks exist, compatibility statements should remain explicit and
evidence-based.

## Automated visibility

`meta.scad-projects` generates a daily repository-status report. It compares
the gitlink pinned in the meta repository with the current default branch and
reports the latest stable semantic-version tag where one exists.

This report is observational: it does not automatically advance or commit
submodule pointers. Use `update-repos.ps1` / `update-repos.sh` when an ecosystem
snapshot is intentionally advanced.
