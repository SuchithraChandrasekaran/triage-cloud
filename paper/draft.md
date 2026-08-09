# Triage-Cloud: An Event-Driven Framework for Cost, Failure-Risk, and
# Architecture-Aware Cloud Provisioning

**Author:** Suchithra Chandrasekaran
*Independant Researcher*

---

## Abstract

Cloud cost governance tools today are reactive: they report overspending,
recommend optimizations, or flag anomalies only after resources have
already been provisioned. Deployment failure patterns are rarely checked
against historical incident data before a new deployment is attempted, and
architecture choices such as CPU instance family are often made by default
rather than measured workload fit. This paper presents triage-cloud, an
event-driven framework that evaluates cost, failure risk, and architecture
fit together, at deployment time, before provisioning occurs. The
framework combines a deterministic keyword-based check with an LLM-based
semantic check for failure-pattern matching, and adds an agentic
investigation layer that autonomously decides whether an unmatched message
represents a novel failure pattern worth flagging for human review. The
system produces three distinct decision outcomes - APPROVE, FLAG, and
BLOCK - rather than a binary allow/deny. We evaluate the system across 20
scenarios spanning budget, failure-pattern, and architecture-fit checks
(100% correct after fixing seven real defects found during testing), a
10-case targeted false-positive analysis (5 of 10 synthetic negation/
past-tense messages were misclassified, with the semantic layer
responsible for 4 of the 5), and a baseline comparison showing that
single-signal gating strategies miss failure incidents entirely. We
report all results, including the two-thirds of false positives that
prompt-level fixes did not fully resolve, as an honest account of where a
keyword-plus-LLM approach remains fragile.

**Keywords:** Cloud Computing, Infrastructure as Code, FinOps, Cost
Governance, Failure Prevention, Agentic AI, Cloud Architecture

---

## I. Introduction

Cloud cost alerts such as AWS Budgets and Cost Anomaly Detection notify
teams after spending has already occurred; nothing in the deployment
pipeline itself checks budget status before a resource is provisioned.
Deployment failure patterns recur across projects, yet this knowledge is
rarely consulted automatically before a new deployment is attempted.
Architecture decisions such as instance family selection are frequently
made by default rather than backed by workload-specific performance data.
AWS's own recently launched FinOps Agent exemplifies the current state of
the art: it investigates cost anomalies and surfaces recommendations, but
is explicitly designed to keep a human in the loop for every action,
rather than intervening at deployment time.

No existing framework evaluates budget status, failure risk, and
architecture fit together, at the point of deployment, before
infrastructure is provisioned. This paper addresses that gap, and extends
it further with two additional contributions motivated during development:
a semantic (LLM-based) failure-matching layer to address the brittleness
of pure keyword matching, and an agentic layer that autonomously decides
how to handle failure patterns not present in the existing knowledge base.

Our contributions are:
1. An event-driven architecture unifying cost, failure-risk, and
   architecture-fit checks into a single deployment-time decision with
   three distinct outcomes (approve, flag, block).
2. A dual failure-matching approach combining deterministic keyword
   matching with LLM-based semantic matching, evaluated head-to-head.
3. An agentic investigation layer that autonomously flags novel failure
   patterns for human review rather than acting unilaterally on
   low-confidence signals.
4. An empirical CPU benchmark informing architecture-fit decisions.
5. An honest, evidence-based account of the system's real limitations,
   including a targeted false-positive analysis showing where semantic
   matching introduces failure modes that keyword matching does not.

---

## II. Related Work

Automated FinOps data-standardization approaches use large language
models to unify multicloud billing data into a common format, but focus
on collecting and standardizing cost data rather than acting on it at
deployment time [1]. Automation-focused FinOps studies address real-time
resource tracking and post-hoc decommissioning of underutilized resources,
acting after waste has already occurred rather than preventing it [2].
Agent-based approaches apply autonomous AI agents to retrieve and analyze
cost data and generate optimization recommendations, but still require a
human to review and act on the output [3]. Cost-aware elastic provisioning
work optimizes instance selection using live spot pricing, achieving
substantial savings, but considers cost in isolation [4]. Earlier
cost-aware elasticity systems similarly optimize server configuration for
cost and reconfiguration time as a single-signal problem [5]. Most
recently, AWS's own FinOps Agent investigates cost anomalies and surfaces
recommendations through chat and ticketing integrations, explicitly
designed to keep a human in the loop rather than enforce decisions
automatically [6].

Across all six sources, each addresses one signal - cost tracking, cost
recommendation, or cost-based provisioning - in isolation, and each acts
reactively. Triage-cloud combines budget status, failure-risk history, and
architecture fit into a single pre-deployment decision, and further
distinguishes itself by combining deterministic and LLM-based matching
with an autonomous review-flagging layer, rather than relying on a single
detection method or a purely human-driven recommendation loop as in [3]
and [6].

---

## III. Methodology

### A. Architecture Overview

Triage-cloud consists of four stages: an Event Source (AWS Budgets and
Cost Anomaly Detection publishing to SNS), a Knowledge Base (DynamoDB
tables for budget tracking, failure modes, and a review queue), a
Decision Engine (an AWS Lambda function performing five checks in
sequence), and Enforcement (Terraform, gated by the decision output).

### B. Failure-Mode Knowledge Base

Fifteen failure modes were catalogued across the evaluation period (eleven
initially, four more added when testing revealed they existed in project
documentation but had not been loaded into the operational knowledge
base), drawn from AWS free-tier quota documentation and a prior enterprise
cloud replatforming project.

### C. Dual Failure-Pattern Matching

Two independent checks run on every incoming message. The **keyword
check** performs case-insensitive substring matching against each
knowledge-base entry's failure type, affected resource, and
comma-separated cause phrases (checked individually, after testing showed
that treating a multi-clause cause field as one continuous string caused
real messages to go unmatched). A **negation guard** was added after
testing revealed false positives: if the message contains resolution or
negation language (e.g., "resolved," "no issues," "successfully"), the
keyword check is skipped for that message. The **semantic check** sends
the message and the full failure-mode list to a Groq-hosted Llama 3.1 8B
model, instructed to identify a match only if the message describes an
active, current problem, explicitly excluding resolved or negated
framing. Either check returning a match is sufficient to block the
deployment.

### D. Agentic Investigation Layer

When neither the keyword nor semantic check finds a match, an agent - a
separate LLM call with a distinct prompt - independently decides whether
the message plausibly describes a genuinely new failure pattern worth
human review, or is a normal, non-failure message. If it decides to flag
the message, it autonomously writes a candidate entry, with its own
generated reasoning, to a review-queue table. This is a decision and an
action taken by the model, not a fixed classification returned to
predetermined code branches: the system does not tell the agent what to
write or when to write it, only that a review-queue table exists as an
available action.

### E. Architecture-Fit Benchmark

A Monte Carlo pi-estimation workload (20,000,000 sample points) was run
on `t3.micro` (x86) and `t4g.micro` (ARM/Graviton) instances.

### F. Decision Logic

The engine evaluates, in order: (1) budget status - if current spend
strictly exceeds the budget limit, BLOCK; (2) failure-pattern match (either
check) - if matched, BLOCK; (3) if neither matched, the agentic layer runs
and may FLAG; (4) otherwise, APPROVE, with an architecture suggestion
(ARM by default, x86 if the message signals urgency).

---

## IV. Results

### A. Architecture Benchmark

| Instance | Type | Time (s) |
|---|---|---|
| t3.micro | x86 | 5.51 |
| t4g.micro | ARM (Graviton) | 5.86 |

x86 completed the benchmark approximately 6% faster than ARM for this
CPU-bound workload, motivating a conditional rather than blanket
architecture-fit rule.

### B. Decision Engine Evaluation (20 scenarios)

| Metric | Result |
|---|---|
| Cost-overrun prevention rate | 4/4 (100%) |
| Failure-prevention rate | 9/9 (100%) |
| Architecture-fit accuracy | 7/7 (100%) |
| **Overall** | **20/20 (100%)** |

Fourteen of twenty scenarios passed on the first run. Six required a fix:
one matching-logic defect (cause phrases not split individually), four
knowledge-base entries that existed in project documentation but had not
been loaded into the operational DynamoDB table, and one architecture-fit
trigger-word list too narrow to catch phrasing such as "quickly" or
"time-sensitive." All six were corrected based on the evaluation evidence
itself, and all twenty scenarios subsequently passed. We report the
first-try and post-fix figures together rather than only the final 100%,
since the initial failures are informative evidence of where a
keyword-matching and rule-based approach is fragile.

The system was also verified end-to-end against live AWS infrastructure:
a routine, budget-compliant message correctly produced APPROVE, followed
by a successful `terraform apply`; a message matching a known failure
pattern correctly produced BLOCK with no infrastructure change applied.

### C. False Positive Analysis

Ten synthetic messages were hand-crafted (not drawn from production
traffic) to probe whether the system would incorrectly block safe
deployments that mention failure-related terms in a resolved, negated, or
past-tense context. Table III summarizes the outcomes after the negation
guard and revised AI prompt were applied.

**Table III: False Positive Test Results**

| # | Pattern probed | Keyword | Semantic (Groq) | Result | False Positive |
|---|---|---|---|---|---|
| 1 | Past-tense, named failure type | No match | Matched | BLOCK | Yes |
| 2 | Unrelated safe message | No match | No match | APPROVE | No |
| 3 | Negated ("no issues found") | No match | No match | APPROVE | No |
| 4 | Past-tense, resolution language | No match | Matched | BLOCK | Yes |
| 5 | Negation phrasing not in guard list | Matched | No match | BLOCK | Yes |
| 6 | Past-tense ("fixed last week") | No match | Matched | BLOCK | Yes |
| 7 | Negated, ambiguous phrasing | No match | No match | FLAG | Borderline |
| 8 | Negated, unrelated resource | No match | No match | APPROVE | No |
| 9 | Negation ("never an issue") | No match | Matched | BLOCK | Yes |
| 10 | Negation ("audit passed") | No match | No match | APPROVE | No |

Five of ten targeted probes produced false positives. After the negation
guard was added to the keyword check, four of the five remaining false
positives originated from the semantic (Groq) layer, not the keyword
layer - a reversal of the layers' relative reliability from what the
initial design assumed. This indicates that explicit prompt instructions
alone did not fully suppress the model's tendency to match on the
presence of a named failure type regardless of surrounding negation, and
that a purely rule-based negation guard, while limited in coverage, was
more reliable than instructing an LLM to reason about negation for this
task.

### D. Baseline Comparison

Derived from the real budget and failure outcomes already recorded across
the 20-scenario evaluation (Section IV-B), rather than from new synthetic
runs:

| Configuration | Cost overruns allowed through | Failure incidents allowed through |
|---|---|---|
| No gating | 1/1 (100%) | 8/8 (100%) |
| Budget-only gating | 0/1 (0%) | 8/8 (100%) |
| Triage-cloud (full) | 0/1 (0%) | 0/8 (0%) |

Budget-only gating, while catching the cost case, misses every
failure-pattern case entirely, demonstrating that the framework's value
comes specifically from checking multiple signals rather than any single
one in isolation.

---

## V. Discussion

The architecture benchmark result illustrates that a single workload type
does not generalize to a universal "ARM is better" claim; the current
rule is deliberately workload-signal-dependent rather than absolute.

The false-positive analysis is, in our view, the paper's most informative
result precisely because it is not a clean success. Two rounds of fixes -
a negation-aware keyword guard and an explicitly negation-instructed LLM
prompt - resolved three of the original ten probes but left five
unresolved, four of them attributable to the semantic layer continuing to
match on a named failure type despite explicit instructions to consider
tense and negation. We interpret this as evidence that prompt-level
instruction is an insufficient substitute for structured reasoning about
negation, and that a production version of this system would likely need
either a dedicated negation-classification step prior to matching, or a
more capable/fine-tuned model than the 8B free-tier model used here.

**Limitations.** All evaluation in this paper - the 20 core scenarios and
the 10 false-positive probes - uses hand-crafted synthetic messages rather
than production traffic; a production-scale evaluation is left to future
work. The failure-mode knowledge base (15 entries) was built from one
practitioner's prior incident experience and public documentation, and
its coverage of the broader space of cloud deployment failures is
necessarily incomplete. The agentic layer's flagging decisions were not
independently validated against ground truth beyond the single test
case reported; a larger-scale evaluation of agent flagging precision is
future work. The Groq free-tier API used for the semantic and agentic
layers introduced integration friction during development (a
non-obvious 403 error traced to Lambda's default HTTP client header
being treated as bot-like traffic), which is documented here as a
practical implementation note for others building similar systems.

---

## VI. Conclusion

This paper presented triage-cloud, an event-driven framework combining
budget, failure-risk, and architecture-fit checks with a dual
keyword-plus-LLM matching approach and an autonomous investigation agent,
producing three distinct decision outcomes rather than a binary gate. We
reported a complete evaluation, including cases where the system did not
initially work as intended and the fixes applied, and a targeted
false-positive analysis showing that semantic matching, while catching
cases keyword matching misses, introduces its own distinct and only
partially correctable failure mode around negation. Future work includes
a dedicated negation-classification step, production-scale evaluation,
and expansion of the failure-mode knowledge base beyond a single
practitioner's incident history.

---

## References

[1] Automating FinOps in Cloud Computing: An Integrated Solution for
    Efficient Data Collection with Dynamic Scraper Generation, *2024 IEEE
    International Conference on Cloud Computing Technology and Science
    (CloudCom)*, Abu Dhabi, UAE, Dec. 2024.

[2] D. Burke, "Improving FinOps Procedures with Automation Tools and
    Framework Changes for a Cloud Environment," M.S. thesis, School of
    Electrical Engineering, Aalto University, 2024.

[3] N. P. A. Vo, M. Kesarwani, R. Mahindru, and C. Narayanaswami, "FinOps
    Agent — A Use-Case for IT Infrastructure and Cost Optimization,"
    *arXiv:2510.25914 [cs.AI]*, Oct. 2025.

[4] "Cost-Aware Elastic Cloud Provisioning for Scientific Workloads,"
    *2015 IEEE 8th International Conference on Cloud Computing*, 2015.

[5] "Kingfisher: Cost-Aware Elasticity in the Cloud," *2011 Proceedings
    IEEE INFOCOM*, Shanghai, China, Apr. 2011.

[6] Amazon Web Services, "AWS FinOps Agent," announced June 2026.
    [Online]. Verify exact citation format and URL before submission.

---
