# Architecture — Day 5

Four stages, left to right, with one feedback loop back to the start.

## 1. Event source
Where things begin. AWS Budgets and Cost Anomaly Detection watch spending and
fire an event when something needs a decision (approaching budget, unusual
spend, a new deployment request).

## 2. Knowledge base
Two lookup tables in DynamoDB:
- Project → budget → current spend
- Known failure patterns (from FAILURE-MODES.md)

The decision engine checks against these before making any call.

## 3. Decision engine
A Lambda function that checks three things for every deployment request:
- Is this project within budget?
- Does this match a known failure pattern?
- Is there a better architecture choice (ARM vs x86) for this workload?

Returns one of: approve, block, or downgrade/reroute.

## 4. Enforcement
The decision gets applied to the actual infrastructure — a Terraform apply
step that either goes ahead, gets blocked, or gets adjusted based on what
the decision engine returned.

## Feedback loop
Once a deployment happens, the outcome (did it fail, what did it cost) feeds
back into the knowledge base tables, so the system's checks get better
informed over time instead of staying static.
