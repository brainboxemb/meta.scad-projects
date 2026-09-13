# New chat / work-session handoff

Use this page when continuing the cross-project tooling roadmap in a new ChatGPT
conversation. The meta repository is the coordination source; implementation
belongs in the repository named as owner of the selected plan step.

A handoff must not assume that the architecture is unchanged since the previous
work session. New shared tooling can change repository ownership boundaries and
may require correcting the plan before the selected implementation step starts.

## Copy/paste start instruction

Replace `<N>` and the step name with the step you want to continue.

```text
Werk vanuit meta.scad-projects als cross-project coordination source.

Lees eerst de actuele cross-project context:
- docs/architecture.md
- docs/repository-map.md
- docs/project-workflow-model.md
- docs/tooling-test-plan.md

Controleer vóór implementatie of de gekozen stap, owner en afhankelijkheden nog
passen bij de actuele architectuur. Als een nieuwe repository of gewijzigde
ownership-boundary het plan raakt, corrigeer dan eerst het plan en pak de
noodzakelijke prerequisite op voordat je de oorspronkelijke stap vervolgt.

Ga verder met Step <N> — <step name>.

Gebruik voor de implementatie de repository die bij die stap als owner staat.
Pak nog geen latere stappen op, behalve als de huidige stap een correctie van
het plan noodzakelijk maakt.

Bij een cross-project migratie van CAD/SCAD repositories:
- gebruik tech.scad/catalog.yml als brede bron voor de project-infrastructure
  generation/classificatie;
- neem niet aan dat alle CAD repositories dezelfde infrastructuur gebruiken;
- houd classic projecten buiten scope tenzij hun migratie expliciet onderdeel
  van de stap is.

Na implementatie:
- controleer de tests/evidence die bij die stap horen;
- werk de status/evidence van de stap in meta.scad-projects bij waar dat nuttig
  is;
- houd implementatiedetails in de repository die eigenaar is van de stap.
```

## Current prerequisite

The introduction of `tool.git-project` changed the ownership boundary of the
current project stack. Generic Git bootstrap/dependency/submodule management is
now owned by `tool.git-project`; SCAD-specific build, design and verification
behavior remains owned by `tool.scad-project`.

Therefore Structured build-decision telemetry must not continue until the
bootstrap ownership/adoption prerequisite in `tooling-test-plan.md` is complete.

A current handoff should therefore use the prerequisite step from that plan,
not the older direct Step 1 instruction.

## Why tech.scad is part of migration scoping

`meta.scad-projects` owns the controlled integration set and cross-project plan.
It deliberately does not catalog every CAD repository.

`tech.scad` owns the wider repository catalog and project-infrastructure
classification. Its `catalog.yml` distinguishes current projects from classic
standalone/shared-actions projects. Use that classification to establish the
broad candidate set for a migration, while each individual repository remains
authoritative for its actual adoption state.

## Working rule

A new chat should not reconstruct the architecture from prior chat history.
Start with the current architecture/repository-map plus the workflow and plan
documents, select one bounded step, and use the owning repository for
implementation. If those documents expose a changed prerequisite or ownership
boundary, correct the plan first.

`meta.scad-projects` remains the place for the cross-project plan, status and
stable conclusions. `tech.scad` remains the broader catalog; neither replaces
the implementation documentation in the owning repositories.
