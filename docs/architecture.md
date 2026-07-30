# Architecture — Day 5 (updated Day 9)

Four stages, left to right, with one feedback loop back to the start.

## 1. Event source
Where things begin. AWS Budgets and Cost Anomaly Detection watch spending and
publish alerts to an SNS topic (`triage-cloud-budget-topic`, Standard type)
when something needs a decision.

## 2. Knowledge base
Two lookup tables in DynamoDB:
- Project → budget → current spend
- Known failure patterns (from FAILURE-MODES.md)

The decision engine checks against these before making any call.

## 3. Decision engine
A Lambda function, subscribed directly to the SNS topic, that checks three
things for every deployment request:
- Is this project within budget?
- Does this match a known failure pattern?
- Is there a better architecture choice (ARM vs x86) for this workload?

Returns one of: approve, block, or downgrade/reroute.

Note: SNS publishes straight to this Lambda (no EventBridge hop needed) — EventBridge alerts don't carry the actual budget message content,
so a direct SNS subscription is the simpler, correct path here.

## 4. Enforcement
The decision gets applied to the actual infrastructure — a Terraform apply
step that either goes ahead, gets blocked, or gets adjusted based on what
the decision engine returned.

## Feedback loop
Once a deployment happens, the outcome (did it fail, what did it cost) feeds
back into the knowledge base tables, so the system's checks get better
informed over time instead of staying static.
