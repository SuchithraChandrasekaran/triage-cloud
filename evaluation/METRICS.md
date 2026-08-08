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
real gaps in its own setup, and those gaps got fixed based on test evidence.
