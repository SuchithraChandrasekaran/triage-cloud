# Benchmark Plan — Day 4

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

## Local baseline (WSL, not part of the real comparison)
- Points used: 20,000,000
- Pi estimate: 3.1409308
- Time taken: 6.32 seconds

This local run is only a reference point to confirm the script works correctly.
The real comparison happens on actual AWS instances (Day 22: x86, Day 23: ARM).

--------------------------------------------------------------
