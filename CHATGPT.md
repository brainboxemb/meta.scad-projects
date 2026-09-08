# CHATGPT.md

## Repository purpose

`meta.scad-projects` is the central architecture, repository-map and cross-project
integration-context repository for the SCAD ecosystem.

It exists so that ecosystem-level design decisions do not live only in chat
history or become duplicated inconsistently across repositories.

## Current repositories

- `docker.scad-toolchain`
- `docker.scad-toolchain.test`
- `tool.scad-project`
- `template.scad-project`
- `lib.scad.clamps`

## Repository ownership model

Each underlying repository remains authoritative for its own implementation,
tests and release history.

This repository is authoritative for:

- ecosystem architecture
- cross-repository dependency relationships
- compatibility/version mapping
- integration conventions
- overkoepelende design documentation

Do not move implementation code here merely to centralize it.

## Diagram convention

Prefer Mermaid embedded directly in Markdown for architecture diagrams.

Reasons:

- text based
- Git diff friendly
- directly rendered by GitHub
- easy to update alongside architecture changes

Use yEd/GraphML only when a graph becomes complex enough that interactive
layout adds real value. In that case GraphML is source and PNG/SVG is generated
output.

## Source/build separation

Normal branch:

```text
Markdown
Mermaid
configuration
submodule pointers
```

Generated branch:

```text
generated diagrams
integration reports
generated cross-project documentation
```

Use `build` as the mutable generated branch unless a later ecosystem-wide
decision changes the convention.

## Submodules

The repositories under `repos/` are intended to be real Git submodules in the
actual Git repository.

The ZIP representation cannot encode gitlinks, so `.gitmodules` plus bootstrap
scripts are included. Bootstrap must stay Python-free and require only Git plus
PowerShell/bash.

## Current architecture

Runtime:
- `docker.scad-toolchain`

Runtime consumer validation:
- `docker.scad-toolchain.test`

Reusable project workflow:
- `tool.scad-project`

Reference consumer:
- `template.scad-project`

Reusable CAD library:
- `lib.scad.clamps`

Integration/architecture:
- `meta.scad-projects`

## Near-term roadmap

1. Establish this repository and pin the current ecosystem repositories.
2. Keep architecture and repository map current.
3. Update `lib.scad.clamps` to the generated design-documentation model.
4. Add integration checks only after the source-of-truth documentation is
   stable enough to define what should be checked automatically.
