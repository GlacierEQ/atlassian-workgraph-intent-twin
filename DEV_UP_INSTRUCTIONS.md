# DEV_UP_INSTRUCTIONS — implementation record

**Repository:** `GlacierEQ/atlassian-workgraph-intent-twin`  
**Independent company lens:** Atlassian  
**Innovation:** Workgraph Intent Twin

## Implemented

The scaffold has been replaced by a multi-object workgraph intent verifier. It validates object scope, allowed/forbidden fields, status constraints, dependency ordering, required acceptance tests and blast radius; it rejects cycles, missing dependencies, scope expansion, status drift and missing/failed tests with structured findings and deterministic digests.

`src/workgraph_intent_cli.py` and `scripts/operate.py` execute the verifier directly. The project is packaged with `workgraph-intent-twin`.

## Verification contract

Behavioral tests cover aligned changes, out-of-scope objects, forbidden/unapproved fields, invalid status, unsatisfied dependency, missing test, failed test and cyclic intent graphs. Existing adversarial coverage remains active.

CI must pass tests, cold-start, wheel build/install and installed CLI execution before Helix promotion evidence is minted.

## Truth boundary

No Atlassian affiliation, proprietary access, production deployment, customer impact, or company partnership is claimed. A real Jira/Confluence change adapter remains a further deployment step.
