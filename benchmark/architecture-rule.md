# Architecture Rule — Day 25

Based on what I found on Day 24: x86 was a bit faster (5.51s vs 5.86s), but
ARM usually costs less per hour. So the rule isn't "always use ARM" - it
depends on what matters more for the job.

## The rule
- If the workload needs to finish as fast as possible → use x86 (t3.micro)
- If the workload can take a little longer but cost matters more → use ARM (t4g.micro)
- If neither is specified → default to ARM, since the cost difference usually
  outweighs a small speed difference for everyday batch jobs

## How this fits into the decision engine
When a deployment request comes in, the engine checks if the request mentions
a preference (speed vs cost). If it does, apply the matching rule above. If
not, default to ARM.

This rule is a first guess, not a perfect answer. 
It's built from one test, so it's good enough to start using right now,
but later on — once more kinds of workloads get tested — 
the rule can be made smarter and more accurate.
