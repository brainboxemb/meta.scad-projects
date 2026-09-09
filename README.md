# meta.scad-projects

Central architecture, repository map, integration context and cross-project
documentation for the SCAD project ecosystem.

This repository is the overkoepelende source of truth for the relationships
between the repositories that make up the SCAD tooling and library workflow.

## Scope

The repository documents and integrates:

- `docker.scad-toolchain`
- `docker.scad-toolchain.test`
- `tool.scad-project`
- `template.scad-project`
- `lib.scad.clamps`

The individual repositories remain independently versioned and own their own
implementation details. This repository documents how they fit together.

## Tracked repositories

| Repository | Role |
| --- | --- |
| [`docker.scad-toolchain`](https://github.com/brainboxemb/docker.scad-toolchain) | Runtime / build environment |
| [`docker.scad-toolchain.test`](https://github.com/brainboxemb/docker.scad-toolchain.test) | Verification of the runtime/toolchain |
| [`tool.scad-project`](https://github.com/brainboxemb/tool.scad-project) | Reusable project and build tooling |
| [`template.scad-project`](https://github.com/brainboxemb/template.scad-project) | Reference consumer project |
| [`lib.scad.clamps`](https://github.com/brainboxemb/lib.scad.clamps) | Reusable CAD library |

The current generated overview of pinned commits, latest default-branch commits,
tags and GitHub Actions state is published on the generated `build` branch:

[Repository status](https://github.com/brainboxemb/meta.scad-projects/blob/build/repository-status.md)

## Repository roles

```mermaid
flowchart TD

    subgraph RUNTIME["Runtime / Build environment"]
        direction TB
        TOOLCHAIN["docker.scad-toolchain"]
    end

    subgraph WORKFLOW["Project workflow"]
        direction TB
        TOOL["tool.scad-project"]
    end

    subgraph DESIGN["Design / Consumers"]
        direction TB
        TEMPLATE["template.scad-project"]
        CLAMPS["lib.scad.clamps"]
    end

    subgraph VERIFY["Verification"]
        direction TB
        TOOLCHAIN_TEST["docker.scad-toolchain.test"]
    end

    TEMPLATE -->|"build tooling"| TOOL
    TEMPLATE -->|"runtime"| TOOLCHAIN
    TEMPLATE -->|"design / reusable CAD"| CLAMPS

    TOOL -->|"runs on"| TOOLCHAIN

    TOOLCHAIN_TEST -.->|"verifies"| TOOLCHAIN
```

See [docs/architecture.md](docs/architecture.md) for the full ecosystem view.

## Project dependency model

Consumer projects now describe their dependency policy in `project.yml`.

Example:

```yaml
tooling:
  tool_scad_project:
    type: git-submodule
    url: https://github.com/brainboxemb/tool.scad-project.git
    path: tools/tool.scad-project
    ref: v0.6.0

externals:
  - name: lib.scad.clamps
    type: git-submodule
    url: https://github.com/brainboxemb/lib.scad.clamps.git
    path: dsg/openscad/ext/lib.scad.clamps
    ref: main
```

The configured `ref` is dependency policy, while the parent repository's Git
submodule gitlink is the concrete lock.

Supported policy forms are:

```text
ref: vX.Y.Z
    exact released tag

ref: latest
    highest stable semantic-version tag

ref: main
ref: develop
    current head of an explicitly named branch
```

`latest` never silently falls back to `main`.

The current reference projects deliberately demonstrate different behavior:

- `tool.scad-project` is pinned by an exact released ref;
- `template.scad-project` currently follows `lib.scad.clamps` through
  `ref: main`, because that library does not yet have an established release
  tag series;
- a future consumer can use `ref: latest` once the dependency has stable
  semantic-version releases.

Repository setup/update commands are intentionally separated:

```text
bootstrap
    establish/repair submodule registrations and restore committed gitlinks

repo-sync
    restore the exact commits already locked by a consumer repository

update-repo
    intentionally resolve configured refs and advance consumer gitlinks
```

The root `bootstrap.*` and `update-repo.*` scripts supplied by
`tool.scad-project` are Python-free and require only Git plus PowerShell/bash.
The updater leaves changes uncommitted for review.

GitHub Actions reusable workflow refs remain literal YAML values, so
`update-repo` also aligns thin workflow callers with the resolved
`tool.scad-project` ref.

## Source and generated content

The architecture follows the same source/build separation used by the project
tooling:

```text
main
    architecture source
    Markdown
    Mermaid diagrams
    repository metadata
    submodule pointers

build
    generated diagrams
    generated reports
    generated cross-project documentation
```

Generated files should not be committed to the normal source branch unless they
are intentionally maintained source assets.

## Repository layout

```text
meta.scad-projects/
├── repos/                  # Git submodules
├── docs/
│   ├── architecture.md
│   ├── repository-map.md
│   ├── build-model.md
│   └── versioning.md
├── design/
│   └── design.md
├── bootstrap.ps1
├── bootstrap.sh
├── .gitmodules
├── README.md
└── CHATGPT.md
```

## Bootstrap

The ZIP cannot contain real Git submodule gitlinks. After creating the actual
Git repository, run the bootstrap script to register and initialize the
repositories listed in `.gitmodules`.

Windows:

```powershell
.\bootstrap.ps1
```

Linux/macOS:

```bash
bash ./bootstrap.sh
```

The bootstrap scripts require only Git plus PowerShell or bash.


## Direct-submodule rule

The ecosystem now uses a consistent direct-only checkout rule.

```text
normal project/repository operation
    initialize only direct submodules owned by that repository

dependency consumed inside another repository
    do not automatically initialize that dependency's own submodules

full recursive checkout
    only in an explicit integration test
```

For `meta.scad-projects`, this means normal bootstrap, validation and status
workflows materialize only `repos/*`. Nested tooling/libraries inside those
repositories are intentionally left untouched.

## Meta checkout depth

The normal meta workflows intentionally initialize only the first-level
repositories under `repos/`.

```yaml
with:
  submodules: true
```

They do **not** use recursive submodule checkout.

This is intentional because `meta.scad-projects` observes and compares the
tracked repositories; it does not need to materialize every consumer's nested
dependency tree. For example:

```text
meta.scad-projects
└── repos/template.scad-project
    ├── tools/tool.scad-project
    └── dsg/openscad/ext/lib.scad.clamps
        └── tools/tool.scad-project
```

Recursively checking out that full tree makes an observational status workflow
depend on every nested gitlink being remotely available.

A future dedicated integration job may use recursive checkout when the purpose
is specifically to validate complete consumer dependency trees.

## Automated ecosystem status

`.github/workflows/repository-status.yml` generates a current cross-repository
status report:

```text
bld/
├── repository-status.md
└── repository-status.mmd
```

It runs:

- after a push to `main`;
- once per day at `05:17 UTC`;
- on manual `workflow_dispatch`.

The report includes:

- commit pinned by this meta repository;
- remote default branch;
- latest default-branch commit;
- latest stable semantic-version tag;
- whether the pinned commit is current;
- latest completed GitHub Actions result;
- latest commit date;
- a version-labelled Mermaid architecture diagram.

The generated output is published to the mutable orphan `build` branch. Nothing
generated by this workflow is committed to `main`.

## Update all repositories

After bootstrap, the meta repository keeps exact Git submodule commits pinned.
To intentionally move all tracked repositories to the latest commit on their
remote default branch, run:

Windows:

```powershell
.\update-repos.ps1
```

Linux/macOS:

```bash
bash ./update-repos.sh
```

The update script:

- initializes missing submodules first;
- refuses to update a repository that has local changes;
- fetches and prunes `origin`;
- follows each repository's `origin/HEAD` default branch instead of assuming
  that every repository uses `main`;
- updates with `pull --ff-only`;
- prints old and new commit SHAs;
- leaves the changed submodule pointers uncommitted in `meta.scad-projects`.

This keeps the actions separate:

```text
bootstrap
    restore the versions pinned by meta.scad-projects

update-repos
    intentionally advance the tracked repositories

git commit
    accept the new ecosystem snapshot
```

A typical update therefore ends with:

```powershell
git status
git add repos
git commit -m "Update SCAD ecosystem repositories"
```

## Current status

The repository now documents the shared dependency-policy model, reusable workflow architecture, generated-output model and cross-repository status automation. Cross-repository compatibility checks can be added later without turning this meta repository into a runtime dependency.

The model, code and documentation are being developed with the assistance of
ChatGPT.
