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
