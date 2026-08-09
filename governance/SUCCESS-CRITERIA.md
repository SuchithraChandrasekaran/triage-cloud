# Success Criteria — triage-cloud

## What "success" means for this system
1. No deployment proceeds while its project is over budget.
2. No deployment proceeds if it matches a known failure pattern, with
   reasonable confidence.
3. Every deployment that proceeds gets an architecture suggestion backed
   by real benchmark data, not a guess.
4. Cases the system isn't sure about get flagged for a human, not silently
   approved or silently blocked.
5. Every decision is logged and traceable - budget check, failure check,
   architecture check, and final decision, in that order, for every event.

## What this project does NOT claim
- It does not claim production-grade reliability - all evaluation used
  synthetic test messages, not live production traffic.
- It does not claim zero false positives - 5 of 10 targeted negation/
  past-tense probes were misclassified, and this is documented, not hidden.
- It does not claim the failure-mode knowledge base is comprehensive -
  15 entries, drawn from one practitioner's experience plus public docs.

## How success was measured
- 20 core scenarios across budget, failure, and architecture checks
  (100% correct after fixing 7 real defects found during testing)
- 10 targeted false-positive probes (5/10 misclassified, documented as a
  known limitation)
- Baseline comparison showing the combined system catches incidents that
  single-signal gating (budget-only) misses entirely
