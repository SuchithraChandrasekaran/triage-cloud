# Benchmark Plan — Day 4 (updated Day 23)

## Workload
Monte Carlo Pi Estimation — a CPU-bound benchmark (20,000,000 random points).
Chosen because it's a well-known, reproducible benchmark that isolates raw CPU
performance, with no external data files or dependencies needed.

Script: `benchmark/benchmark.py`

## Instances being compared
- **x86:** t3.micro
- **ARM (Graviton):** t4g.micro

## What's measured
- Time taken to complete (printed by the script)
- Cost per run (instance hourly rate x time taken, converted to a per-run cost)

## Local baseline (WSL, reference only, not part of the real comparison)
- Time taken: 6.32 seconds

## Real result — x86 (t3.micro), Day 22
- Pi estimate: 3.1415016
- Time taken: 5.51 seconds

## Real result — ARM (t4g.micro), Day 23
- Pi estimate: 3.1416904
- Time taken: 5.86 seconds

## Early observation
For this specific CPU-bound workload, x86 (t3.micro) was slightly faster than
ARM (t4g.micro) - 5.51s vs 5.86s. This goes against the common assumption
that ARM/Graviton is always faster or more efficient.

## Findings (Day 24)
I ran the same script on both instance types. x86 finished in 5.51 seconds,
ARM finished in 5.86 seconds. So x86 was a bit faster this time, which
surprised me - I expected ARM to win since that's what most people say.

But that's not true. ARM instances usually cost less per hour than
x86 ones, so even though ARM took a little longer, it might still end up
cheaper overall. I haven't done that cost math yet.

Key takeaway: don't just pick ARM because everyone says it's
better. It depends on what the job actually needs - speed or lower cost.
