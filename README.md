# Workgraph Intent Twin

Independent GlacierEQ portfolio implementation aligned to **Atlassian** operating themes.

> **Not affiliated.** This repository is not affiliated with, endorsed by, employed by, or deployed at Atlassian. No proprietary access, production deployment, customer impact, or company partnership is claimed.

## Purpose

Keep agent-driven Jira/document changes aligned with the original multi-object objective as work fans out across tickets, docs, dependencies, statuses, and acceptance tests.

## Implemented twin

`WorkgraphIntentTwin` validates a machine-readable intent contract containing:

- admitted work objects and kinds;
- allowed and forbidden fields per object;
- allowed status transitions;
- dependency edges;
- required acceptance tests;
- maximum change-set blast radius.

A proposed workgraph change is refused for out-of-scope objects, forbidden or unapproved fields, status drift, unsatisfied dependencies, missing/failed required tests, oversized blast radius, duplicate changes, or cyclic/missing dependency definitions. The receipt carries deterministic intent and change-set digests plus structured findings.

## Run

```bash
python -m pytest -q
python scripts/operate.py
```

Build/install:

```bash
python -m pip install build
python -m build
python -m pip install dist/*.whl
workgraph-intent-twin
```

## Proof surface

- `src/workgraph_intent_twin.py` — graph/intent/acceptance verifier
- `src/workgraph_intent_cli.py` — installable execution surface
- `tests/test_workgraph_intent_twin.py` — scope, field, status, dependency, acceptance and cycle behavior
- `.github/workflows/tests.yml` — tests + cold-start + wheel build/install + installed CLI
- `machine/` — existing Helix control-plane/promotion surfaces remain preserved

## Current boundary

This is a vendor-neutral verifier over normalized workgraph changes. It does not mutate Atlassian systems. A further deployment step is a Jira/Confluence adapter that compiles real issue/document deltas into this contract and blocks writes when intent drift is detected.
