# Project Plan — Day 7

## What's built so far (Phase 1, Days 1-6)
- Day 1: Problem statement written (PROBLEM.md) — reactive cost alerts, repeated failures,
  no data-backed architecture choice
- Day 2: Related work scanned (RELATED-WORK.md) — 6 sources reviewed, gap confirmed: nothing
  checks cost + failure risk + architecture fit together, before deployment
- Day 3: Failure mode list written (FAILURE-MODES.md) — 11 failure types from own AWS/FedEx
  experience and free-tier docs
- Day 4: Benchmark plan set (BENCHMARK-PLAN.md) — Monte Carlo Pi estimation, t3.micro vs
  t4g.micro, local baseline run at 6.32 seconds
- Day 5: Architecture drawn (architecture.md) — 4 stages: event source, knowledge base,
  decision engine, enforcement, with a feedback loop
- Day 6: AWS project set up — Zero spend budget alert configured, tagging convention decided
  (Project = triage-cloud)

## What's next (Phase 2)
Build the actual event pipeline: AWS Budgets + Cost Anomaly Detection feeding into
EventBridge, then a Lambda function that receives and logs those events.

## Governance rules 
- A project counts as over budget once it crosses its Zero Spend alert
- A deployment request that matches a known failure pattern from FAILURE-MODES.md gets blocked
- No architecture rule yet 
