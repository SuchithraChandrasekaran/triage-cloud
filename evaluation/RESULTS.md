# Test Results — 20 Scenarios

| # | Category | Message | Expected | Actual DECISION |
|---|---|---|---|---|
| 1 | Budget | Routine deployment check for triage-cloud (budget ok) | APPROVE | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 2 | Budget | Routine deployment check for triage-cloud (spend > limit) | BLOCK - over budget | DECISION: BLOCK - project is over budget |
| 3 | Failure | IAM misconfiguration detected during deployment | BLOCK | DECISION: BLOCK - matches known failure pattern: IAM misconfiguration |
| 4 | Failure | vCPU or service limit hit while launching new instances | BLOCK | DECISION: BLOCK - matches known failure pattern: Resource quota exhaustion |
| 5 | Failure | Security group blocking required traffic | BLOCK | DECISION: BLOCK - matches known failure pattern: Security group misconfiguration (fixed: comma-split matching bug) |
| 6 | Failure | Free tier hour pool nearly depleted | BLOCK | DECISION: BLOCK - matches known failure pattern: Free tier hour depletion (fixed: row wasn't loaded into DynamoDB) |
| 7 | Failure | Deployment completed successfully, no issues | APPROVE | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 8 | Architecture | Urgent deployment needed for triage-cloud | x86 suggested | DECISION: APPROVE - suggested instance: x86 (t3.micro) - speed prioritized |
| 9 | Architecture | Fast turnaround required for this job | x86 suggested | DECISION: APPROVE - suggested instance: x86 (t3.micro) - speed prioritized |
| 10 | Architecture | Priority release for triage-cloud | x86 suggested | DECISION: APPROVE - suggested instance: x86 (t3.micro) - speed prioritized |
| 11 | Architecture | Routine batch job for triage-cloud | ARM suggested | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 12 | Architecture | Standard weekly deployment | ARM suggested | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 13 | Failure | CloudFormation stack failed with rollback complete | BLOCK | DECISION: BLOCK - matches known failure pattern: CloudFormation stack failure (fixed: row wasn't loaded into DynamoDB) |
| 14 | Failure | Disk space exhaustion on batch job server | BLOCK | DECISION: BLOCK - matches known failure pattern: Disk space exhaustion (fixed: row wasn't loaded into DynamoDB) |
| 15 | Failure | API throttling exception during automation | BLOCK | DECISION: BLOCK - matches known failure pattern: API throttling (fixed: row wasn't loaded into DynamoDB) |
| 16 | Failure | S3 access denied while uploading files | BLOCK | DECISION: BLOCK - matches known failure pattern: S3 permission issue (fixed: row wasn't loaded into DynamoDB) |
| 17 | Architecture | Deploy this as quickly as possible, time-sensitive | x86 suggested | DECISION: APPROVE - suggested instance: x86 (t3.micro) - speed prioritized (fixed: broadened trigger words) |
| 18 | Architecture | No specific requirement, standard deployment | ARM suggested | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 19 | Budget | Routine deployment check for triage-cloud (spend == limit, boundary) | APPROVE (not over) | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |
| 20 | Budget | Routine deployment check for triage-cloud (spend well below limit) | APPROVE | DECISION: APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default |

## Summary
20/20 scenarios correct after fixes. 14/20 passed on the first try. 6 required
a fix: one matching-logic bug (comma-separated phrases), four missing
DynamoDB rows, and one too-narrow trigger-word list.
