# Issue contract — Workgraph Intent Twin

## Problem
Agent-driven Jira/Confluence changes lose intent alignment as workflows fan out across tickets and docs.

## Desired outcome
A bounded, open, testable implementation of **Workgraph Intent Twin** that demonstrates Maintain a machine-readable intent twin for each change set and continuously compare patches against forbidden surfaces and acceptance tests.

## Non-goals
- Atlassian affiliation or proprietary integration
- Portfolio-wide scale/performance claims
- UI marketing site

## Acceptance
1. Mechanism module implements allow + refuse with structured receipts
2. pytest behavioral suite green
3. operate.py cold-start produces JSON receipt
4. Non-affiliation disclaimer preserved
