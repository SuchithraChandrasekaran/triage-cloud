# Test Results — Day 32

| # | Category | Message | Expected | Actual DECISION |
|---|---|---|---|---|
| 1 | Budget | Routine deployment check for triage-cloud (budget ok) | APPROVE | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 2 | Budget | Routine deployment check for triage-cloud (spend > limit) | BLOCK - over budget | DECISION: BLOCK - project is over budget |
| 3 | Failure | IAM misconfiguration detected during deployment | BLOCK | DECISION: BLOCK - matches known failure pattern: IAM misconfiguration |
| 4 | Failure | vCPU or service limit hit while launching new instances | BLOCK | DECISION: BLOCK - matches known failure pattern: Resource quota exhaustion |
| 5 | Failure | Security group blocking required traffic | BLOCK | DECISION: BLOCK - matches known failure pattern: Security group misconfiguration |
| 6 | Failure | Free tier hour pool nearly depleted | BLOCK | DECISION: BLOCK - matches known failure pattern: Free tier hour depletion |
| 7 | Failure | Deployment completed successfully, no issues | APPROVE | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 8 | Architecture | Urgent deployment needed for triage-cloud | x86 suggested |DECISION: APPROVE - suggested instance: x86 (t3.micro) - speed prioritized |
| 9 | Architecture | Fast turnaround required for this job | x86 suggested | DECISION: APPROVE - suggested instance: x86 (t3.micro) - speed prioritized |
| 10 | Architecture | Priority release for triage-cloud | x86 suggested | DECISION: APPROVE - suggested instance: x86 (t3.micro) - speed prioritized |
| 11 | Architecture | Routine batch job for triage-cloud | ARM suggested | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 12 | Architecture | Standard weekly deployment | ARM suggested | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
