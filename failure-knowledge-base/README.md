# Failure Knowledge Base

Failure table in DynamoDB plus Lambda logic that checks incoming messages
against known failure causes, types, and affected resources.

## What was learned
Simple keyword matching needs to check the cause text too, not just
failure_type or resource_affected — real messages describe causes, not
category labels. Fixed after a test message matched the wrong
way at first.

## Files in this folder
- `failure-table.md` — the 11 failure types, written out as a table
- (DynamoDB table `triage-cloud-failure-modes` holds the same data, loaded
  from this table)
