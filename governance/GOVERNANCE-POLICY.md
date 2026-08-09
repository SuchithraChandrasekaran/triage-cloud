# Governance Policy — triage-cloud

## Budget policy
A project is considered over budget when its current spend strictly
exceeds its budget limit (current_spend > budget_limit). Spend equal to
the limit is treated as still within budget - a deliberate boundary
choice, tested on Day 32/extended (row 19).

## Failure policy
A deployment is blocked if either the keyword check or the semantic
(Groq) check finds a match to a known failure pattern. Either check
alone is sufficient - the system is deliberately biased toward blocking
over approving when there's disagreement between the two checks, since a
false block is lower-cost than a missed failure.

A negation guard exists on the keyword check: if a message contains
resolution or negation language, the keyword check is skipped for that
message, so as not to block deployments describing already-resolved
issues. The semantic check is separately instructed to make the same
distinction, though testing showed this instruction is only partially
effective (5 of 10 negation-style test messages were still
misclassified - see METRICS.md for the full breakdown).

## Uncertain-case policy (agentic layer)
When neither check finds a match, the system does not default to a
silent approval. An agent independently evaluates whether the message
describes a plausible new failure pattern, and if so, flags it to a
review queue with its own reasoning, rather than blocking or approving
unilaterally. This is intentional: an AI making a low-confidence call
should escalate to a human, not act alone.

## Architecture policy
Instance-type suggestions default to ARM (Graviton) for cost, and switch
to x86 only when the message signals urgency (fast/urgent/priority/
quickly/time-sensitive/asap/immediately). This default was chosen because
the empirical benchmark showed only a 6% time difference between the two
architectures for the tested workload, while ARM pricing is typically
lower - so cost-optimization is the safer default absent a stated urgency
signal.

## Priority order when checks conflict
Budget check runs first and can block outright, regardless of what the
failure or architecture checks find - unless a project is over budget,
nothing else matters. Failure check runs second - a known failure
pattern blocks regardless of architecture considerations. Architecture
suggestions are only made once budget and failure checks are both clear.
This ordering reflects the AHP-derived weighting in AHP-WEIGHTING.md.
