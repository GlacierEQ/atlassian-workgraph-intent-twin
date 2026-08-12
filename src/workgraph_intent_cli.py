from __future__ import annotations

import argparse
import json
from pathlib import Path

from workgraph_intent_twin import Decision, WorkgraphIntentTwin, WorkgraphIntentTwinRequest


def demo_payload() -> dict:
    return {"intent_contract":{"objective":"ship migration","max_changed_objects":2,"required_tests":["contract"],"objects":[{"object_id":"JIRA-1","kind":"issue","allowed_fields":["description","status"],"forbidden_fields":["security_policy"],"allowed_statuses":["Done"],"depends_on":[]}]},"changes":[{"object_id":"JIRA-1","changed_fields":["description","status"],"new_status":"Done","completed_dependencies":[],"content":{"description":"complete"}}],"test_results":[{"test_id":"contract","passed":True}]}


def main() -> int:
    p=argparse.ArgumentParser(description="Verify a workgraph change set against its intent twin")
    p.add_argument("--input",type=Path)
    p.add_argument("--subject",default="workgraph-demo")
    args=p.parse_args()
    payload=json.loads(args.input.read_text()) if args.input else demo_payload()
    receipt=WorkgraphIntentTwin().evaluate(WorkgraphIntentTwinRequest(args.subject,payload,1.0))
    print(json.dumps(receipt.as_dict(),indent=2,sort_keys=True))
    return 0 if receipt.decision is Decision.ALLOW else 2

if __name__=="__main__":
    raise SystemExit(main())
