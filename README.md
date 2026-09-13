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

### Machine–Mesh Protocol Manifest

<!-- glacier-eq-protocol:start -->
```yaml
{
  "schema": "glacier-eq.readme.machine-mesh/v1",
  "repository": {
    "id": "GlacierEQ/atlassian-workgraph-intent-twin",
    "url": "https://github.com/GlacierEQ/atlassian-workgraph-intent-twin",
    "readme_contract": "estate-machine-v1",
    "default_branch": "main"
  },
  "machine": {
    "repository_kind": "migration-residue",
    "public_api": "inspect-declared-entrypoints",
    "protocol_files": [],
    "entrypoints": [
      {
        "kind": "package-contract",
        "path": "pyproject.toml",
        "policy": "inspect-before-use"
      },
      {
        "kind": "source-area",
        "path": "src",
        "policy": "inspect-before-use"
      },
      {
        "kind": "script-area",
        "path": "scripts",
        "policy": "inspect-before-use"
      },
      {
        "kind": "test-area",
        "path": "tests",
        "policy": "run-before-reliance"
      },
      {
        "kind": "machine-contract-area",
        "path": "machine",
        "policy": "read-first"
      }
    ]
  },
  "presentation": {
    "architecture": [
      "recruiter",
      "master",
      "machine",
      "mesh"
    ],
    "authority": {
      "capability": "stone-psysoc-x",
      "repository": "GlacierEQ/AKOS",
      "manifest": "stones/psysoc-x/stone.json",
      "engine": "infinity_stones/psysoc_x.py"
    },
    "truth_invariant": "presentation-may-change-sequence-density-tone-and-style; facts-evidence-uncertainty-provenance-dignity-and-reader-agency-may-not"
  },
  "license": {
    "class": "EXISTING_LICENSE",
    "status": "CONTROLLING_LICENSE_CONTENT_REVIEW_REQUIRED",
    "controlling_path": "LICENSE",
    "policy": "GlacierEQ/job-app-helix/LICENSE_POLICY.json",
    "may_relicense_automatically": false,
    "upstream_rights_must_be_preserved": false
  },
  "mesh": {
    "primary_home": null,
    "branch": "migration-residue",
    "subcategory": "unresolved-primary-home",
    "routing": [
      {
        "relation": "estate-map",
        "target": "GlacierEQ/monolith",
        "url": "https://github.com/GlacierEQ/monolith"
      }
    ],
    "boundaries": [
      "routing-does-not-transfer-source-code-evidence-deployment-or-lifecycle-authority",
      "generated-contract-is-a-source-index-not-a-runtime-or-provider-receipt",
      "implementation-and-provider-state-require-independent-evidence",
      "presentation-calibration-cannot-promote-claim-or-evidence-state",
      "license-automation-cannot-relicense-unresolved-upstream-or-third-party-rights"
    ]
  },
  "provenance": {
    "generated_by": "GlacierEQ/job-app-helix",
    "generator_contract": "estate-machine-v1",
    "classification_source": null,
    "classification_evidence_path": null,
    "classification_evidence_blob_sha": null,
    "classification_status": null,
    "contract_digest": "def7fdf1962e2d56df6416425a4f318f4b36f5ba7854a991ea2a26a5806cf973"
  }
}
```
<!-- glacier-eq-protocol:end -->
