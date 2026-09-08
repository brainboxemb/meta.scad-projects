# Repository map

## Repositories

| Repository | Role | Consumes | Generated branch |
| --- | --- | --- | --- |
| `docker.scad-toolchain` | CAD/runtime image | external packages | image tags |
| `docker.scad-toolchain.test` | runtime consumer tests | `docker.scad-toolchain` | optional reports |
| `tool.scad-project` | reusable project workflow | `docker.scad-toolchain` | `build` |
| `template.scad-project` | reference consumer | toolchain, project tool, libraries | `build` |
| `lib.scad.clamps` | reusable CAD library | toolchain | `build` |
| `meta.scad-projects` | ecosystem architecture/integration | all above as submodules | `build` |

## Integration view

```mermaid
flowchart TB
    OPS[meta.scad-projects]

    OPS -. tracks .-> TOOLCHAIN[docker.scad-toolchain]
    OPS -. tracks .-> TEST[docker.scad-toolchain.test]
    OPS -. tracks .-> TOOL[tool.scad-project]
    OPS -. tracks .-> TEMPLATE[template.scad-project]
    OPS -. tracks .-> CLAMPS[lib.scad.clamps]

    TEST --> TOOLCHAIN
    TOOL --> TOOLCHAIN
    TEMPLATE --> TOOL
    TEMPLATE --> TOOLCHAIN
    TEMPLATE --> CLAMPS
```

The dotted relationships are integration/coordination relationships. They do
not mean that the individual repositories depend on `meta.scad-projects`.
