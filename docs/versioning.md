# Versioning and compatibility

## Independent repository versions

Each repository is independently versioned.

Do not assume that matching version numbers across repositories indicate a
release set.

Example:

```text
docker.scad-toolchain        v0.3.0
tool.scad-project            v0.3.x
template.scad-project        v0.5.x
lib.scad.clamps              independent
```

## Pinned dependencies

Consumer repositories should pin dependencies with Git submodule gitlinks or
explicit immutable image tags.

A submodule entry in `.gitmodules` identifies the repository URL. The parent
repository's Git tree stores the exact dependency commit.

## Compatibility map

As the ecosystem matures, this repository should maintain a tested
compatibility table such as:

| Component | Version | Tested with |
| --- | --- | --- |
| `tool.scad-project` | v0.3.x | `docker.scad-toolchain` v0.3.0 |
| `template.scad-project` | v0.5.x | pinned project tool commit |
| `lib.scad.clamps` | current | toolchain v0.3.0 |

This table should eventually be generated from integration tests rather than
manually guessed.


## Automated visibility

`meta.scad-projects` generates a daily repository-status report. It compares
the gitlink pinned in the meta repository with the current default branch and
shows the newest Git tag.

This report is observational: it does not automatically advance or commit
submodule pointers. Use `update-repos.ps1` / `update-repos.sh` when an update is
intentionally accepted.
