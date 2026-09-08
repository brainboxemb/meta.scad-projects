# Source and build model

## General rule

Source and generated output are deliberately separated.

```text
main
    source code
    source design.md
    configuration
    Mermaid source
    repository metadata

build
    generated PNG/SVG
    generated design documentation
    generated reports
    generated exports
```

## Design documentation

A repository maintains design source on its normal source branch:

```text
design.md
```

Render declarations can be embedded as:

```markdown
<!-- scad-render-defaults
module: example_design
vpr: [65, 0, 35]
-->

<!-- scad-render
view: final
-->
```

The project tooling generates the readable design documentation and images
under `bld/design`.

The generated build branch can then contain:

```text
design/
├── project/
└── ext/
```

This means a consumer can browse generated documentation for its own
components and for compatible external libraries without generated binaries
being committed to the source branch.

## Build and verification branches

`build` is the common mutable generated-output branch.

A repository only needs a separate `verification` branch when its verification
evidence has a distinct lifecycle from normal generated build output.

Current examples:

```text
template.scad-project
    main
    build

lib.scad.clamps
    main
    build
    verification
```

`lib.scad.clamps` uses `verification` for functional/API consumer evidence.
The template does not add a separate verification branch merely for symmetry.

Common GitHub Actions build logic belongs in reusable workflows under
`tool.scad-project`. Consumer repositories keep thin workflow callers.

## Meta repository

The same principle applies here.

Mermaid embedded in Markdown is source and renders directly on GitHub.

If the ecosystem later needs exported PNG/SVG diagrams or generated integration
reports, those should be written to `bld/` and published to the generated
`build` branch.
