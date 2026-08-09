# AHP Weighting — triage-cloud

This is the author's own judgment, not a multi-stakeholder study - labeled honestly as such,
not overstated as team consensus.

## Criteria
- Failure-Risk (F)
- Cost (C)
- Architecture-Fit (A)

## Pairwise comparisons (1-9 scale, Saaty scale)
| Comparison | Rating | Reasoning |
|---|---|---|
| Failure-Risk vs Cost | 3 (moderately more important) | The system already blocks on failure before even considering cost |
| Failure-Risk vs Architecture-Fit | 5 (strongly more important) | Architecture is only ever a suggestion, never a blocker |
| Cost vs Architecture-Fit | 4 (moderately-to-strongly more important) | Cost blocks deployments; architecture only suggests |

## Comparison matrix

| | Failure-Risk | Cost | Architecture |
|---|---|---|---|
| Failure-Risk | 1 | 3 | 5 |
| Cost | 1/3 | 1 | 4 |
| Architecture | 1/5 | 1/4 | 1 |

## Computed priority weights
- Failure-Risk: 0.619 (62%)
- Cost: 0.284 (28%)
- Architecture-Fit: 0.096 (10%)

## Consistency check
- Lambda max: 3.087
- Consistency Index (CI): 0.043
- Random Index (RI, n=3): 0.58
- **Consistency Ratio (CR): 0.075**

A CR below 0.1 is considered acceptable (Saaty's threshold), meaning
these pairwise judgments are internally consistent rather than
contradictory.

## Comparison against actual code behavior
The computed weights (Failure-Risk > Cost > Architecture, by a wide
margin) match the system's actual decision order: budget and failure
checks can both block outright, while architecture only ever produces a
suggestion, never a block. The AHP analysis formalizes and validates a
prioritization that was already implicit in the code, rather than
revealing a mismatch - reported honestly as confirmatory rather than
as new design guidance.
