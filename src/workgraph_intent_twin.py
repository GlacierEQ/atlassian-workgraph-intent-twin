"""Workgraph Intent Twin.

Verifies a multi-object workgraph change set against a machine-readable intent
contract. It catches scope expansion, forbidden field mutation, dependency-order
violations, status drift, and missing/failed acceptance tests before a Jira/doc
workflow can be called aligned with the original objective.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


class Decision(str, Enum):
    ALLOW = "ALLOW"
    REFUSE = "REFUSE"


@dataclass(frozen=True)
class WorkgraphIntentTwinRequest:
    subject_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    budget: float = 1.0
    grant_id: str | None = None
    not_after: float | None = None


@dataclass(frozen=True)
class WorkgraphIntentTwinReceipt:
    decision: Decision
    reasons: tuple[str, ...]
    digest: str
    metrics: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"decision": self.decision.value, "reasons": list(self.reasons), "digest": self.digest, "metrics": self.metrics}


class WorkgraphError(ValueError):
    pass


class WorkgraphIntentTwin:
    MIN_BUDGET = 0.0

    @staticmethod
    def _id(value: Any, label: str) -> str:
        value = str(value or "").strip()
        if not value:
            raise WorkgraphError(f"{label}_missing")
        return value

    @staticmethod
    def _string_set(value: Any, label: str, *, allow_empty: bool = False) -> set[str]:
        if not isinstance(value, list):
            raise WorkgraphError(f"{label}_not_list")
        result = {str(v).strip() for v in value if str(v).strip()}
        if not result and not allow_empty:
            raise WorkgraphError(f"{label}_missing")
        return result

    @classmethod
    def _contract(cls, raw: Any) -> dict[str, Any]:
        if not isinstance(raw, dict):
            raise WorkgraphError("intent_contract_missing")
        objects_raw = raw.get("objects")
        if not isinstance(objects_raw, list) or not objects_raw:
            raise WorkgraphError("intent_objects_missing")
        objects: dict[str, dict[str, Any]] = {}
        for index, item in enumerate(objects_raw):
            if not isinstance(item, dict):
                raise WorkgraphError(f"intent_object_{index}_not_object")
            object_id = cls._id(item.get("object_id"), f"intent_object_{index}_id")
            if object_id in objects:
                raise WorkgraphError(f"duplicate_intent_object:{object_id}")
            objects[object_id] = {
                "object_id": object_id,
                "kind": cls._id(item.get("kind"), f"intent_object_{index}_kind"),
                "allowed_fields": cls._string_set(item.get("allowed_fields", []), f"intent_object_{index}_allowed_fields", allow_empty=True),
                "forbidden_fields": cls._string_set(item.get("forbidden_fields", []), f"intent_object_{index}_forbidden_fields", allow_empty=True),
                "allowed_statuses": cls._string_set(item.get("allowed_statuses", []), f"intent_object_{index}_allowed_statuses", allow_empty=True),
                "depends_on": cls._string_set(item.get("depends_on", []), f"intent_object_{index}_depends_on", allow_empty=True),
            }
        for object_id, item in objects.items():
            missing = item["depends_on"] - set(objects)
            if missing:
                raise WorkgraphError(f"intent_dependency_missing:{object_id}:{','.join(sorted(missing))}")
        indegree = {k: 0 for k in objects}
        children: dict[str, list[str]] = defaultdict(list)
        for object_id, item in objects.items():
            for parent in item["depends_on"]:
                indegree[object_id] += 1
                children[parent].append(object_id)
        queue = deque(sorted(k for k, v in indegree.items() if v == 0))
        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            for child in sorted(children[node]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        if visited != len(objects):
            raise WorkgraphError("intent_dependency_cycle")
        return {
            "objective": cls._id(raw.get("objective"), "intent_objective"),
            "objects": objects,
            "required_tests": cls._string_set(raw.get("required_tests", []), "required_tests", allow_empty=True),
            "max_changed_objects": int(raw.get("max_changed_objects", len(objects))),
        }

    @classmethod
    def _changes(cls, raw: Any) -> list[dict[str, Any]]:
        if not isinstance(raw, list) or not raw:
            raise WorkgraphError("changes_missing")
        changes: list[dict[str, Any]] = []
        seen: set[str] = set()
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                raise WorkgraphError(f"change_{index}_not_object")
            object_id = cls._id(item.get("object_id"), f"change_{index}_object_id")
            if object_id in seen:
                raise WorkgraphError(f"duplicate_change_object:{object_id}")
            seen.add(object_id)
            changes.append({
                "object_id": object_id,
                "changed_fields": cls._string_set(item.get("changed_fields", []), f"change_{index}_changed_fields", allow_empty=True),
                "new_status": str(item.get("new_status") or "").strip() or None,
                "completed_dependencies": cls._string_set(item.get("completed_dependencies", []), f"change_{index}_completed_dependencies", allow_empty=True),
                "content_digest": _digest(item.get("content", {})),
            })
        return changes

    @classmethod
    def _tests(cls, raw: Any) -> dict[str, bool]:
        if raw is None:
            return {}
        if not isinstance(raw, list):
            raise WorkgraphError("test_results_not_list")
        result: dict[str, bool] = {}
        for index, item in enumerate(raw):
            if not isinstance(item, dict):
                raise WorkgraphError(f"test_result_{index}_not_object")
            test_id = cls._id(item.get("test_id"), f"test_result_{index}_id")
            if test_id in result:
                raise WorkgraphError(f"duplicate_test_result:{test_id}")
            result[test_id] = item.get("passed") is True
        return result

    def evaluate(self, req: WorkgraphIntentTwinRequest) -> WorkgraphIntentTwinReceipt:
        reasons: list[str] = []
        if not str(req.subject_id or "").strip():
            reasons.append("subject_id_missing")
        if isinstance(req.budget, bool) or not isinstance(req.budget, (int, float)) or not math.isfinite(float(req.budget)) or float(req.budget) <= self.MIN_BUDGET:
            reasons.append("budget_non_positive_or_invalid")
        payload = req.payload if isinstance(req.payload, dict) else {}
        if not isinstance(req.payload, dict):
            reasons.append("payload_not_object")
        findings: list[dict[str, Any]] = []
        result: dict[str, Any] | None = None
        try:
            contract = self._contract(payload.get("intent_contract"))
            changes = self._changes(payload.get("changes"))
            test_results = self._tests(payload.get("test_results"))
            if len(changes) > contract["max_changed_objects"]:
                findings.append({"kind": "blast_radius_exceeded", "count": len(changes), "limit": contract["max_changed_objects"]})
            for change in changes:
                object_id = change["object_id"]
                expected = contract["objects"].get(object_id)
                if expected is None:
                    findings.append({"kind": "object_outside_intent_scope", "object_id": object_id})
                    continue
                forbidden = change["changed_fields"] & expected["forbidden_fields"]
                outside_allowed = change["changed_fields"] - expected["allowed_fields"] if expected["allowed_fields"] else set()
                if forbidden:
                    findings.append({"kind": "forbidden_field_changed", "object_id": object_id, "fields": sorted(forbidden)})
                if outside_allowed:
                    findings.append({"kind": "field_outside_allowed_surface", "object_id": object_id, "fields": sorted(outside_allowed)})
                if change["new_status"] and expected["allowed_statuses"] and change["new_status"] not in expected["allowed_statuses"]:
                    findings.append({"kind": "status_outside_intent", "object_id": object_id, "status": change["new_status"]})
                missing_dependencies = expected["depends_on"] - change["completed_dependencies"]
                if missing_dependencies:
                    findings.append({"kind": "dependency_not_satisfied", "object_id": object_id, "dependencies": sorted(missing_dependencies)})
            missing_tests = sorted(test_id for test_id in contract["required_tests"] if test_id not in test_results)
            failed_tests = sorted(test_id for test_id in contract["required_tests"] if test_results.get(test_id) is False)
            if missing_tests:
                findings.append({"kind": "required_test_missing", "tests": missing_tests})
            if failed_tests:
                findings.append({"kind": "required_test_failed", "tests": failed_tests})
            changed_ids = sorted(change["object_id"] for change in changes)
            result = {
                "aligned": not findings,
                "objective": contract["objective"],
                "changed_objects": changed_ids,
                "findings": findings,
                "required_tests": sorted(contract["required_tests"]),
                "passed_required_tests": sorted(test_id for test_id in contract["required_tests"] if test_results.get(test_id) is True),
                "intent_digest": _digest({"objective": contract["objective"], "objects": {k: {x: sorted(v[x]) if isinstance(v[x], set) else v[x] for x in v} for k, v in sorted(contract["objects"].items())}, "required_tests": sorted(contract["required_tests"]), "max_changed_objects": contract["max_changed_objects"]}),
                "change_set_digest": _digest(changes),
            }
            if findings:
                reasons.append("workgraph_intent_drift_detected")
        except WorkgraphError as exc:
            reasons.append(str(exc))
        decision = Decision.REFUSE if reasons else Decision.ALLOW
        metrics = {"result": result, "finding_count": len(findings)}
        body = {"subject_id": req.subject_id, "decision": decision.value, "reasons": reasons, "metrics": metrics}
        return WorkgraphIntentTwinReceipt(decision, tuple(reasons or ["workgraph_change_aligned_with_intent"]), _digest(body), metrics)


Mechanism = WorkgraphIntentTwin
