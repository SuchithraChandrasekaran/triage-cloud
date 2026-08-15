# Metrics — Day 31

Three things I'm measuring to prove the system actually works, not just that
it runs.

## 1. Cost-overrun prevention rate
Out of test cases where the project is over budget, what percent did the
system correctly BLOCK.

## 2. Failure-prevention rate
Out of test cases that mention a known failure pattern, what percent did
the system correctly catch and BLOCK.

## 3. Architecture-fit accuracy
Out of test cases where the message clearly signals speed matters ("fast",
"urgent") or cost matters (no signal, default case), what percent got the
expected instance suggestion (x86 for speed, ARM for cost/default).

## How this gets measured
Day 32: run 10-15 test messages through the Lambda, covering all three
categories above, and record what the system decided for each one.
Day 33: calculate the percentages from that data.

## Final Results (Day 33)

| Metric | Result |
|---|---|
| Cost-overrun prevention rate | 2/2 = 100% |
| Failure-prevention rate | 5/5 = 100% |
| Architecture-fit accuracy | 5/5 = 100% |
| **Overall** | **12/12 = 100%** |

## Honest note
2 of the 12 tests (rows 5 and 6) only passed after fixes made during testing:
row 5 needed the failure-matching logic fixed (comma-separated cause phrases
weren't being split and checked individually), and row 6 needed a missing
failure mode to actually be loaded into DynamoDB (it existed in
FAILURE-MODES.md but was never added to the table). Reporting 100% without
this context would be misleading - the real story is that the system caught
real gaps in its own setup, and those gaps got fixed based on test evidence,
not guesswork.

## Extended Results (20 scenarios total)

| Category | Tests | Passed (first try) | Passed (after fix) | Final Rate |
|---|---|---|---|---|
| Cost-overrun prevention | 4 | 4 | 4 | 100% |
| Failure-prevention | 9 | 4 | 9 | 100% |
| Architecture-fit | 7 | 6 | 7 | 100% |
| **Total** | **20** | **14** | **20** | **100%** |

7 real gaps were found and fixed across the full 20-scenario run:
1. Comma-separated cause phrases weren't matched individually (Day 32)
2. Free tier depletion failure mode wasn't loaded into DynamoDB (Day 32)
3. CloudFormation stack failure wasn't loaded into DynamoDB
4. Disk space exhaustion wasn't loaded into DynamoDB
5. API throttling wasn't loaded into DynamoDB
6. S3 permission issue wasn't loaded into DynamoDB
7. Architecture trigger words were too narrow ("quickly"/"time-sensitive" not caught)

Two budget boundary cases were also tested: current_spend equal to budget_limit
(correctly treated as within budget, not blocked) and current_spend well below
budget_limit (correctly approved).

## False Positive Analysis (3 targeted tests)

Three messages were deliberately constructed to test whether the system
would incorrectly block safe deployments that mention failure-related
keywords in a non-threatening context (past tense, negation).

| Message | Keyword | AI (Groq) | Result | False Positive |
|---|---|---|---|---|
| "Successfully resolved the IAM misconfiguration issue yesterday" | Matched | Matched | BLOCK | Yes |
| "Security training completed, no security group changes needed" | No match | No match | APPROVE | No |
| "Quota review completed, no vCPU or service limit issues found" | No match | Matched | BLOCK | Yes |

2 of 3 targeted tests produced false positives, each through a different
mechanism. Neither the keyword matcher nor the semantic (Groq) matcher
currently accounts for tense or negation - both react to the presence of
failure-related terms regardless of whether the surrounding sentence
describes an active problem or a resolved/non-issue. This is a genuine,
documented limitation, not a rare edge case: any message referencing past
incidents or explicitly ruling out an issue is at risk of being misread.

## Baseline Comparison (derived from the same 20 real test scenarios)

Rather than running new scenarios, this compares three gating strategies
against the same 20 real messages already tested, by re-applying simpler
rules to the same real budget/failure data already recorded.

| Configuration | Cost overruns allowed through | Failure incidents allowed through |
|---|---|---|
| No gating (approve everything) | 1/1 (100%) | 8/8 (100%) |
| Budget-only gating | 0/1 (0%) | 8/8 (100%) |
| triage-cloud (full system) | 0/1 (0%) | 0/8 (0%) |

This is derived from the actual real outcomes already logged for each of
the 20 scenarios (Section: Extended Results), not new synthetic runs. It
shows that budget-only gating, while catching the cost case, misses every
failure-pattern case entirely - the combined approach's value comes
specifically from checking multiple signals rather than any single one in
isolation.

## Extended False Positive Analysis (10 targeted tests)

Ten synthetic messages were hand-crafted to probe negation and past-tense
framing - not drawn from production traffic. Five produced false positives.

| # | Message | Keyword | AI (Groq) | Result | False Positive |
|---|---|---|---|---|---|
| 1 | Successfully resolved IAM issue | No match | Matched | BLOCK | Yes (AI) |
| 2 | Security training, no changes needed | No match | No match | APPROVE | No |
| 3 | Quota review, no issues found | No match | No match | APPROVE | No |
| 4 | Disk space issue, now resolved | No match | Matched | BLOCK | Yes (AI) |
| 5 | No API throttling detected | Matched | No match | BLOCK | Yes (keyword, pre-fix gap) |
| 6 | CloudFormation failure, fixed last week | No match | Matched | BLOCK | Yes (AI) |
| 7 | IAM setup, no misconfig expected | No match | No match | FLAG | Borderline (flagged, not blocked) |
| 8 | Free tier healthy, no concerns | No match | No match | APPROVE | No |
| 9 | Security group rules never an issue | No match | Matched | BLOCK | Yes (AI) |
| 10 | IAM audit passed, no misconfigurations | No match | No match | APPROVE | No |

After the negation-aware keyword fix, every false positive except one
(#5, a phrasing gap in the negation guard) came from the AI (Groq) layer,
not the keyword layer. This is a notable, non-obvious finding: the
semantic matching layer, intended to catch cases keyword matching missed,
is also the primary remaining source of false positives once keyword
matching is made negation-aware. Both matching strategies have real,
distinct failure modes rather than one being strictly superior.

## Statistical Confidence Intervals (Wilson score, 95%)

Given the modest sample sizes in this evaluation (20 core scenarios, 10
false-positive probes), a Wilson score confidence interval is reported
rather than a p-value, which would misrepresent the statistical power of
a sample this small. The Wilson interval is a standard, appropriate
method for binomial proportions at small n.

| Metric | Result | 95% Wilson CI |
|---|---|---|
| Cost-overrun prevention | 4/4 (100%) | [51.0%, 100.0%] |
| Failure-prevention | 9/9 (100%) | [70.1%, 100.0%] |
| Architecture-fit accuracy | 7/7 (100%) | [64.6%, 100.0%] |
| Overall (20 scenarios) | 20/20 (100%) | [83.9%, 100.0%] |
| False-positive probes (correct) | 5/10 (50%) | [23.7%, 76.3%] |

The wide intervals at small subgroup sizes (e.g., cost-overrun prevention
at only n=4) are expected and are reported honestly rather than omitted -
a 100% result on 4 trials genuinely carries wide uncertainty, and stating
the interval rather than the point estimate alone avoids overstating
confidence in results with this little data. The false-positive interval
in particular ([23.7%, 76.3%]) is wide enough to make clear that the true
false-positive rate could plausibly range from roughly one-quarter to
three-quarters of cases - a large enough range that no strong claim about
the semantic layer's real-world reliability should be drawn from this
sample alone. Larger-scale evaluation is needed before this system's
false-positive rate could be stated with statistical confidence.

## Cost-Per-Invocation Analysis

Computed from real billed-duration values recorded in CloudWatch logs
during testing (AWS Lambda pricing, us-east-1, 128 MB memory, on-demand,
$0.0000166667 per GB-second + $0.0000002 per request).

| Configuration | Avg billed duration | Cost per invocation |
|---|---|---|
| Keyword-only checks (no AI call) | 886 ms | $0.000002045 |
| With Groq AI semantic check | 1,522 ms | $0.000003372 |

The AI layer roughly adds 60% more compute time per invocation, driven by
the external API round-trip. At this duration, AWS's free tier (1M
requests + 400,000 GB-seconds/month) covers approximately 1,000,000
invocations per month at zero cost - well beyond what a project at this
scale would use. Extrapolated to a paid tier for reference: 100,000
invocations/month would cost approximately $0.34; 1,000,000 would cost
approximately $3.37 - the three-way decision gate (skipping the AI call
entirely when a keyword match already found a result) is therefore also
a meaningful cost-efficiency choice at higher volumes, not just a latency
optimization.

## Large-Scale Evaluation (100 real test cases)

Run via an automated batch-testing tool (tools/batch_test.py) that invokes
the real deployed Lambda directly for 100 systematically generated
messages: 48 failure-mode variants (across direct, paraphrase x2,
negated x2, and unrelated phrasing, for 8 confirmed-loaded failure
types), 10 budget boundary cases, 18 architecture-urgency cases, and 24
clean/unrelated messages.

| Category | Correct | Total | Accuracy | 95% Wilson CI |
|---|---|---|---|---|
| Overall | 90 | 100 | 90.0% | [82.6%, 94.5%] |
| Failure matching | 38 | 48 | 79.2% | [65.7%, 88.3%] |
| Budget | 10 | 10 | 100.0% | [72.2%, 100.0%] |
| Architecture | 18 | 18 | 100.0% | [82.4%, 100.0%] |
| Clean/unrelated | 24 | 24 | 100.0% | [86.2%, 100.0%] |

At this larger, more realistic sample size, budget, architecture, and
clean-message handling all remain fully reliable, while failure-pattern
matching drops to 79.2% - a materially different picture than the small
initial samples suggested, and a more honest one. This is the correct,
expected effect of testing at scale: smaller samples can mask real
failure rates that only become visible with more data.

**2 false positives** (both "negated" variants: a resolved IAM issue and
a "no throttling detected" message still matched and blocked) - the
negation guard added earlier reduces but does not eliminate this failure
mode at scale.

**8 false negatives**, concentrated almost entirely in "paraphrase2"
variants - messages describing a real failure using vocabulary not
present in the knowledge base's stored phrasing (e.g., "NACL rules
appear misconfigured" was not recognized as Security group
misconfiguration; "Automation script hitting AWS API rate limits" was
not recognized as API throttling). Notably, several of these
false-negative cases were still caught by the agentic layer, which
independently flagged them for human review rather than silently
approving - a real safety benefit of the three-outcome design even where
the primary matching failed.

**Limitation of this run:** the AI confidence score and per-check match
fields were not captured in this dataset due to a deployment gap - the
enriched Lambda response (added to support ROC/AUC analysis) had not yet
been deployed when this batch was run. A follow-up run is needed to
capture confidence data for a full ROC/AUC curve.
