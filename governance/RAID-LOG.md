# RAID Log — triage-cloud

## Risks (things that could go wrong)
| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Free-tier LLM API (Groq) rate limits or outages during testing | Medium | Medium | Keyword check runs independently, system still functions if AI check fails |
| 2 | Confidence scores from Groq may be inconsistent or poorly calibrated (model just guessing a number) | Medium | Medium | Report ROC/AUC honestly, note calibration as a limitation if scores look arbitrary |
| 3 | Semantic matching false positives remain unresolved at submission | Confirmed (5/10 found) | Medium | Documented honestly as a limitation, not hidden |
| 4 | AHP weighting is solo-author judgment, not multi-stakeholder - may read as less rigorous to reviewers | Confirmed (by design) | Low-Medium | Explicitly labeled as author's own judgment in the paper, not overstated as consensus |
| 5 | Statistical claims (confidence intervals) could be seen as thin given small sample size (30 tests) | Confirmed | Low | Used Wilson score interval (valid for small samples) instead of misleading p-values |

## Assumptions (things taken as true, not yet proven)
| # | Assumption | Status |
|---|---|---|
| 1 | A single CPU-bound benchmark (Monte Carlo Pi) is representative enough to inform architecture-fit rules | Not fully validated — noted as a limitation |
| 2 | 20 hand-crafted test scenarios are sufficient to demonstrate core functionality | Accepted for this paper's scope |
| 3 | Pairwise AHP ratings (failure-risk > cost > architecture) reflect reasonable real-world priority, not just current code behavior | To validate against final computed weights |
| 4 | Groq's confidence score output is meaningful and not just noise | To validate once ROC data is collected |


## Issues (things that have actually gone wrong)
| # | Issue | Found | Resolved | Resolution |
|---|---|---|---|---|
| 1 | DynamoDB Decimal type not JSON serializable | Day 13 | Yes | Added decimal_default() helper |
| 2 | Comma-separated cause phrases matched as one block | Day 32 | Yes | Split and check phrases individually |
| 3 | 4 failure modes documented but never loaded into DynamoDB | Day 32/extended | Yes | Added missing rows |
| 4 | Gemini API persistent 429 rate limiting | Day AI-layer | Yes (switched) | Moved to Groq |
| 5 | Groq 403 Forbidden despite valid key | Day AI-layer | Yes | Added explicit User-Agent header |
| 6 | Semantic layer false positives on negated/past-tense messages | False-positive testing | Partial | Negation guard + prompt fix resolved 3/10; 5/10 remain, documented as limitation |
| 7 | make_decision() function signature accidentally deleted during an agentic-layer code edit | Agentic layer build | Yes | Restored function header, verified with syntax check |
| 8 | DECISION output originally conflated FLAG outcomes into APPROVE text | Agentic layer build | Yes | Split into three distinct outcomes: APPROVE, FLAG, BLOCK |

## Dependencies (things this project relies on)
| # | Dependency | Status |
|---|---|---|
| 1 | AWS Free Tier account limits | Active, monitored via Zero Spend budget |
| 2 | Groq free-tier API availability | Active |
| 3 | IEEE TCC submission portal (ScholarOne) | Account created |
| 4 | Governance/policy framing content |  In progress |
| 5 | AHP consistency-ratio calculation | Pending pairwise inputs |
| 6 | Confidence-interval calculation (Wilson score) | Pending final test counts |
| 7 | Governance/PM artifacts (RAID log, success criteria) | In progress |
