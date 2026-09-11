# New chat / work-session handoff

Use this page when continuing the cross-project tooling roadmap in a new ChatGPT
conversation. The meta repository is the coordination source; implementation
belongs in the repository named as owner of the selected plan step.

## Copy/paste start instruction

Replace `<N>` and the step name with the step you want to continue.

```text
Werk vanuit meta.scad-projects als cross-project coordination source.

Lees:
- docs/project-workflow-model.md
- docs/tooling-test-plan.md

Ga verder met Step <N> — <step name>.

Gebruik voor de implementatie de repository die bij die stap als owner staat.
Pak nog geen latere stappen op, behalve als de huidige stap een correctie van
het plan noodzakelijk maakt.

Na implementatie:
- controleer de tests/evidence die bij die stap horen;
- werk de status/evidence van de stap in meta.scad-projects bij waar dat nuttig
  is;
- houd implementatiedetails in de repository die eigenaar is van de stap.
```

For the next planned implementation step this becomes:

```text
Werk vanuit meta.scad-projects als cross-project coordination source.

Lees:
- docs/project-workflow-model.md
- docs/tooling-test-plan.md

Ga verder met Step 1 — Structured build-decision telemetry.

Gebruik voor de implementatie tool.scad-project.
Pak nog geen latere stappen op, behalve als Step 1 een correctie van het plan
noodzakelijk maakt.

Na implementatie:
- controleer de tests/evidence die bij Step 1 horen;
- werk de status/evidence van Step 1 in meta.scad-projects bij waar dat nuttig
  is;
- houd implementatiedetails in tool.scad-project.
```

## Working rule

A new chat should not reconstruct the architecture from prior chat history.
Start with the two documents above, select one numbered step, and use the owning
repository for implementation. `meta.scad-projects` remains the place for the
cross-project plan, status and stable conclusions.
