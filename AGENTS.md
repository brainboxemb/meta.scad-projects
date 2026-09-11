# Repository agent guidance

Persistent guidance for automated coding agents working in `meta.scad-projects`.

## Repository purpose

`meta.scad-projects` is the central architecture, repository-map and
cross-project integration-context repository for the current SCAD ecosystem.

It exists so ecosystem-level decisions do not live only in chat history or get
duplicated inconsistently across repositories.

## Authority boundary

Each tracked repository remains authoritative for its own implementation,
tests, release history and local documentation.

This repository is authoritative for:

- ecosystem architecture;
- cross-repository dependency relationships;
- integration conventions;
- compatibility/version mapping when derived from real repository state;
- cross-project documentation.

Do not move implementation code here merely to centralize it.

## Sources of truth

Avoid copying volatile versions into this file.

Use:

```text
.gitmodules + gitlinks                 tracked repository set / pinned commits
tracked repositories                   implementation and local dependency policy
scripts/repository-status.py           generated current-state reporting
architecture Markdown/Mermaid          hand-maintained architecture intent
```

Generated status must observe repository state; it must not become a second
hand-maintained dependency database.

## Architecture conventions

Use Mermaid embedded in Markdown for normal architecture diagrams. Prefer
`flowchart TD` for the central ecosystem view.

Group repositories semantically:

```text
Runtime / Build environment
Project workflow
Design / Consumers
Verification
```

Label relationships by purpose (`runtime`, `build tooling`, `design / reusable
CAD`, `runs on`, `verifies`). Use dashed arrows for verification/observation
rather than normal dependencies.

Use GraphML only when a graph becomes complex enough that interactive layout is
materially useful; GraphML is then source and rendered images are generated
output.

## Source/build separation

The normal source branch contains architecture/configuration/submodule pointers.
Generated diagrams, reports and cross-project status belong under generated
output and the configured generated branch, not mixed into source.

## Tracked repositories and submodules

Repositories under `repos/` are real Git submodules in the actual repository.
Normal meta workflows initialize first-level submodules only.

Do not recursively initialize nested consumer dependencies merely to report
meta state. Recursive checkout is reserved for a dedicated integration test
whose explicit purpose is validating complete dependency trees.

Across the ecosystem, normal checkout/update operations should initialize only
direct dependencies owned by the current repository.

## Bootstrap and updates

Keep bootstrap and advancement separate:

```text
bootstrap.ps1 / bootstrap.sh
    establish/restore the committed submodule locks

update-repos.ps1 / update-repos.sh
    fetch direct tracked repositories
    advance only by explicit fast-forward policy
    leave changed gitlinks for human review
```

Update scripts must not reset/force branches or auto-commit meta changes.

## Consumer dependency model

For current SCAD consumers:

```text
project.yml       dependency policy
parent gitlink    exact resolved lock
```

Supported policy forms include exact stable tag, `latest` stable semantic tag,
and explicit branch. Never interpret `latest` as the default branch.

Do not copy current per-repository version pins into this file. Generate or read
them from the owning repositories instead.

Canonical consumer operations remain conceptually distinct:

```text
bootstrap      establish/repair submodules and committed locks
repo-sync      restore committed dependency locks
update-repo    intentionally resolve policy and advance locks
```

Generic consumer workflow logic belongs in `tool.scad-project`; consumers keep
thin callers.

## Status automation

Repository roles and relationships are hand-maintained architecture source.
Changing operational state is generated.

Status automation may report items such as:

- pinned gitlink commit;
- latest remote default-branch commit;
- latest stable semantic tag;
- latest completed Actions result;
- update/up-to-date state.

It must never update or commit submodules automatically. Advancing pins remains
an explicit reviewed operation.

## Relationship with tech.scad

`meta.scad-projects` covers the controlled current infrastructure/integration
set. `tech.scad` is the broader catalog/knowledge layer including classic
infrastructure and user CAD projects.

Do not expand this repository into the broad catalog role already owned by
`tech.scad`.
