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

## Meta repository

The same principle applies here.

Mermaid embedded in Markdown is source and renders directly on GitHub.

If the ecosystem later needs exported PNG/SVG diagrams or generated integration
reports, those should be written to `bld/` and published to the generated
`build` branch.
