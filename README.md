# Triage-Cloud

An agentic AI framework that triages cloud deployment events *before* they cause budget overruns or repeat known failures — checking cost, failure risk, and architecture fit, then approving, flagging, or blocking the deployment.

## How it works

An SNS event (deployment alert, anomaly, etc.) triggers a Lambda that runs three checks:

1. **Budget check** — pulls the project's spend/limit from DynamoDB; blocks if over budget.
2. **Failure pattern check** — dual-path: a keyword match against a known-failures table, plus a semantic check via an LLM (Groq/Llama 3.1), with negation handling so a resolved/fixed issue doesn't trigger a false block.
3. **Architecture fit check** — suggests x86 vs ARM (Graviton) instance type based on urgency signals in the message.

If neither check matches, an agentic step decides whether the event looks like a genuinely new failure pattern worth human review, and writes it to a review queue itself.

Final decision is one of: **APPROVE**, **FLAG**, or **BLOCK**.

## Repo layout

- `event-pipeline/` — the decision-engine Lambda
- `terraform/` — infra-as-code for the test environment
- `benchmark/` — x86 vs ARM CPU benchmark used for the architecture-fit rule
- `failure-knowledge-base/` — known failure patterns table
- `evaluation/` — accuracy/metrics results
- `governance/` — decision-weighting and project governance docs
- `tests/` — unit test suite

