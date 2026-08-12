from __future__ import annotations

from workgraph_intent_twin import Decision, WorkgraphIntentTwin, WorkgraphIntentTwinRequest


def contract():
    return {
        "objective": "ship billing migration without changing security policy",
        "max_changed_objects": 2,
        "required_tests": ["billing-contract", "migration-dry-run"],
        "objects": [
            {"object_id": "JIRA-1", "kind": "issue", "allowed_fields": ["summary", "status", "description"], "forbidden_fields": ["security_policy"], "allowed_statuses": ["In Progress", "Done"], "depends_on": []},
            {"object_id": "DOC-1", "kind": "document", "allowed_fields": ["body", "status"], "forbidden_fields": ["permissions"], "allowed_statuses": ["Draft", "Published"], "depends_on": ["JIRA-1"]},
        ],
    }


def changes():
    return [
        {"object_id": "JIRA-1", "changed_fields": ["description", "status"], "new_status": "Done", "completed_dependencies": [], "content": {"description": "migration complete"}},
        {"object_id": "DOC-1", "changed_fields": ["body", "status"], "new_status": "Published", "completed_dependencies": ["JIRA-1"], "content": {"body": "runbook"}},
    ]


def tests(passed=True):
    return [{"test_id": "billing-contract", "passed": passed}, {"test_id": "migration-dry-run", "passed": True}]


def evaluate(changes_value=None, test_results=None, contract_value=None):
    return WorkgraphIntentTwin().evaluate(
        WorkgraphIntentTwinRequest(
            "workgraph-a",
            {"intent_contract": contract_value or contract(), "changes": changes_value or changes(), "test_results": tests() if test_results is None else test_results},
            1.0,
        )
    )


def finding_kinds(receipt):
    return {row["kind"] for row in receipt.metrics["result"]["findings"]}


def test_aligned_change_set_with_dependencies_and_tests_passes() -> None:
    receipt = evaluate()
    assert receipt.decision is Decision.ALLOW
    assert receipt.metrics["result"]["aligned"] is True
    assert receipt.metrics["finding_count"] == 0
    assert len(receipt.metrics["result"]["intent_digest"]) == 64
    assert len(receipt.metrics["result"]["change_set_digest"]) == 64


def test_object_outside_intent_scope_is_refused() -> None:
    rows = changes() + [{"object_id": "JIRA-999", "changed_fields": ["summary"], "new_status": "Done", "completed_dependencies": [], "content": {}}]
    c = contract(); c["max_changed_objects"] = 3
    receipt = evaluate(rows, contract_value=c)
    assert receipt.decision is Decision.REFUSE
    assert "object_outside_intent_scope" in finding_kinds(receipt)


def test_forbidden_field_change_is_refused() -> None:
    rows = changes(); rows[0]["changed_fields"].append("security_policy")
    receipt = evaluate(rows)
    assert receipt.decision is Decision.REFUSE
    assert "forbidden_field_changed" in finding_kinds(receipt)


def test_field_outside_allowed_surface_is_refused() -> None:
    rows = changes(); rows[0]["changed_fields"].append("assignee")
    receipt = evaluate(rows)
    assert receipt.decision is Decision.REFUSE
    assert "field_outside_allowed_surface" in finding_kinds(receipt)


def test_status_outside_intent_is_refused() -> None:
    rows = changes(); rows[1]["new_status"] = "Archived"
    receipt = evaluate(rows)
    assert receipt.decision is Decision.REFUSE
    assert "status_outside_intent" in finding_kinds(receipt)


def test_dependency_must_be_satisfied_before_downstream_doc_change() -> None:
    rows = changes(); rows[1]["completed_dependencies"] = []
    receipt = evaluate(rows)
    assert receipt.decision is Decision.REFUSE
    assert "dependency_not_satisfied" in finding_kinds(receipt)


def test_missing_required_acceptance_test_is_refused() -> None:
    receipt = evaluate(test_results=[{"test_id": "billing-contract", "passed": True}])
    assert receipt.decision is Decision.REFUSE
    assert "required_test_missing" in finding_kinds(receipt)


def test_failed_required_acceptance_test_is_refused() -> None:
    receipt = evaluate(test_results=tests(passed=False))
    assert receipt.decision is Decision.REFUSE
    assert "required_test_failed" in finding_kinds(receipt)


def test_dependency_cycle_in_intent_contract_fails_closed() -> None:
    c = contract(); c["objects"][0]["depends_on"] = ["DOC-1"]
    receipt = evaluate(contract_value=c)
    assert receipt.decision is Decision.REFUSE
    assert "intent_dependency_cycle" in receipt.reasons
