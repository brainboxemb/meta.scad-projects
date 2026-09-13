# Current SCAD project workflow model

## Purpose

This document records the current project-facing build and verification model
across the SCAD ecosystem.

It is deliberately an **as-is** description. It does not assume that every
current declaration mechanism should remain a separate long-term mechanism.
The improvement plan in [tooling-test-plan.md](tooling-test-plan.md) first makes
build decisions observable and testable, then evaluates whether the authoring
model should be simplified.

A new generic repository/bootstrap layer now exists in `tool.git-project`.
Step 0.5 of the improvement plan migrates current-generation consumers away from
the older `tool.scad-project`-owned bootstrap/dependency behavior before further
build telemetry work continues. This document still describes the current
build/design/verification mechanisms themselves; generic Git bootstrap ownership
is documented in [architecture.md](architecture.md).

Implementation details remain authoritative in the repository that owns them:
generic Git bootstrap/dependency behavior in `tool.git-project`, and SCAD
build/design/verification behavior primarily in `tool.scad-project`. This
document is the cross-project description of how the SCAD mechanisms fit
together.

## Common project foundation

Current-generation consumer projects use a structured source/build/verification
layout, typically:

```text
dsg/                       design/source tree
bld/                       generated normal build output
vrf/                       verification source/evidence
```

Before the Step 0.5 migration is complete, individual consumers may still keep
both generic dependency policy and SCAD-specific project settings together in
`project.yml`. The target ownership split is a generic `project.yml` processed
through `tool.git-project` plus SCAD-specific configuration owned by
`tool.scad-project`; each repository remains authoritative for its actual
migration state.

The selective build backend currently resolves configured work into target
specifications and lets SCons decide whether each target needs execution. The
normal build, design build and verification build have related but distinct
discovery, state and output paths.

The important distinction is therefore between:

```text
authoring / target declaration
        ↓
target discovery / compilation
        ↓
dependency-aware target execution
        ↓
generated output + build decision report
```

The first layer is currently expressed in several different ways.

## Workflow 1 — render and export directories

### Source form

Normal production renders and exports are declared by placing OpenSCAD
entrypoints in configured directories, normally:

```text
dsg/openscad/render/*.scad
dsg/openscad/export/*.scad
```

The SCAD project configuration points at these roots through
`paths.render_root` and `paths.export_root`.

Optional `render.yml` and `export.yml` files add profile information such as:

- size variants;
- image sizes;
- output-name patterns;
- groups of files that share the same profile.

A common pattern is therefore:

```text
dsg/openscad/render/
├── render.yml
├── front.scad
├── rear.scad
└── component.scad

dsg/openscad/export/
├── export.yml
└── component.scad
```

### Generated output

Normal outputs are generated under the project build root, typically:

```text
bld/png/
bld/stl/
```

### Strengths

- source entrypoint to generated artifact is easy to understand;
- production renders and exports are explicit files;
- profile data can describe repeated variants without duplicating every
  entrypoint;
- SCons can track the OpenSCAD dependency graph behind each entrypoint.

### Current friction

- target declaration is partly directory convention and partly YAML profile;
- a loose `.scad` entrypoint is itself part of the build API;
- the declaration model differs from design-document renders and from some
  verification evidence.

## Workflow 2 — design documentation

### Source form

Component design documentation is authored in a `design.md` file, usually near
the component source:

```text
project_components/<component>/design/design.md
```

The Markdown contains narrative design steps plus embedded `scad-render`
declarations. Those declarations describe views, modules, camera settings and
other render-specific information.

Conceptually:

```text
design.md
    narrative
    render declaration 1
    render declaration 2
    ...
        ↓
tooling-generated render entrypoints
        ↓
design SCons execution
```

The generated entrypoints are tooling state; the hand-maintained source remains
`design.md` plus the referenced CAD source.

### Generated output

Readable generated design documentation and its images are written under:

```text
bld/design/
```

This keeps design explanation and design evidence together without committing
generated images to the normal source branch.

### Strengths

- design intent and visual evidence live next to each other;
- a sequence of design views can be documented without maintaining many manual
  render wrapper files;
- generated design evidence follows the same source/build separation as other
  artifacts.

### Current friction

- design render declarations are a different authoring language from
  `render.yml` / `export.yml`;
- the tooling generates intermediate entrypoints that normal project authors do
  not see directly;
- design build state and reporting are related to, but not identical with, the
  normal render/export path.

## Workflow 3 — verification render/export directories

### Source form

Verification-only visual or geometry evidence can be declared through
`verification.render_root` and `verification.export_root`. A common layout is:

```text
vrf/openscad/
├── render.yml              # optional
├── fit-section.scad
├── assembly-check.scad
└── dimension-check.scad
```

Each verification entrypoint becomes verification-only generated evidence.
Profiles can provide variants and output naming in the same general style as
normal render/export roots.

### Generated output

Verification evidence normally goes to:

```text
vrf/out/png/
vrf/out/stl/
```

The verification build uses state/cache paths separate from the normal build so
verification-only evidence does not become a normal production artifact merely
because it was rendered.

### Strengths

- engineering proof can be separated from presentation/production output;
- verification can have its own publication lifecycle;
- the SCons verification cache can be isolated from the normal writable build
  cache.

### Current friction

- verification files are again loose `.scad` entrypoints;
- larger projects sometimes also use project-specific verification scripts,
  which can make it less obvious which layer owns rendering and which layer owns
  assertions;
- verification target discovery is similar to normal rendering, but configured
  and reported separately.

## Workflow 4 — project-specific verification commands

The SCAD project configuration can also declare `verification.commands`. These
commands run after verification target generation and are appropriate for checks
that are not just "render this entrypoint".

Examples include:

- mesh/property checks;
- project-specific dimensional checks;
- verification index generation;
- API or consumer checks;
- additional assertions around generated evidence.

This is useful, but it creates an important boundary that should remain clear:

```text
verification targets
    generate declared evidence

verification commands
    inspect/assert project-specific behavior
```

A project-specific script should not silently become a second unrelated target
orchestration system when the generic verification target model can express the
work.

## Current comparison

| Concern | Normal render/export | Design documentation | Verification evidence |
| --- | --- | --- | --- |
| Primary declaration | `.scad` files in configured directories | `design.md` render directives | `.scad` files in verification directories |
| Extra profile data | `render.yml` / `export.yml` | embedded directive metadata | optional `render.yml` / `export.yml` |
| Main purpose | production/published artifact | explain design evolution | prove behavior/fit/geometry |
| Typical output | `bld/png`, `bld/stl` | `bld/design` | `vrf/out` |
| Selective execution | SCons | design SCons driver | SCons |
| Cache/state | normal build cache/state | design stage using build-side selective cache/state | separate verification cache/state |
| Additional commands | not normally | not normally | `verification.commands` |

The table describes current behavior; it is not a statement that three distinct
internal target models are desirable.

## Current build-decision observability

The current SCons reporting records, at a high level:

```text
executed
not_executed
```

The human-facing workflow summary effectively describes `not_executed` as
"reused/current" or "cache/current".

That is not precise enough for a build system we want to verify formally.
There are at least three materially different outcomes:

```text
BUILT
    the target action executed in this run

CACHE_RESTORED
    the target did not exist before execution and SCons restored it from its
    CacheDir without running the target action

CURRENT
    the target already existed and SCons determined that it was up to date
```

A fourth state is needed for invalid outcomes:

```text
ERROR
    for example, a target was neither executed nor present after the build
```

This distinction is a prerequisite for deterministic cache testing and for a
post-build decision audit.

## GitHub Actions cache layer

The reusable SCAD workflows add a second layer around SCons:

```text
GitHub Actions cache restore
        ↓
SCons local state + CacheDir
        ↓
selective build decision
        ↓
GitHub Actions cache save
```

The workflow currently distinguishes cache-level outcomes such as:

- exact hit;
- fallback hit;
- cold miss.

That information is useful, but it is not the same as the per-target SCons
outcome. A fallback cache hit can still lead to a mixture of targets being
built, restored from SCons cache, or already current.

The long GitHub Actions log is useful for forensic debugging, but it should not
be the primary machine-readable contract for build behavior. Structured build
reports should be the primary evidence, with workflow logs as supporting detail.

## Why the current model feels fragmented

The current system grew useful capabilities incrementally. As a result, the
same broad concept — "declare generated evidence from CAD source" — is exposed
through multiple authoring forms:

```text
render/export directory + profile YAML

design.md + embedded render declarations

verification directory + optional profile YAML

verification commands / project scripts
```

These mechanisms have legitimate domain differences, but the common contract is
not yet explicit enough. In particular:

- target discovery is spread across several conventions;
- cache behavior is observable only coarsely;
- generated reports do not yet explain whether reuse came from current output or
  CacheDir restoration;
- project scripts can overlap with generic target generation;
- workflow YAML tests can prove configuration text without proving actual SCons
  decisions;
- real consumer builds currently act partly as experiments instead of only as
  confirmation of already-defined behavior.

## Desired direction

The target direction is **not** necessarily one authoring syntax for everything.
The more useful architectural goal is one well-defined internal target contract:

```text
normal render/export declarations ─┐
                                   │
design.md render declarations ─────┼─> canonical target specification
                                   │
verification declarations ─────────┘
                                            ↓
                                  dependency-aware execution
                                            ↓
                                  structured decision evidence
```

Domain-specific authoring can remain where it improves usability. The later
roadmap step on authoring-model consolidation will decide which current forms
remain and which duplication can be removed, after build decisions and cache
behavior are covered by deterministic tests.

See [tooling-test-plan.md](tooling-test-plan.md) for that phased plan.
