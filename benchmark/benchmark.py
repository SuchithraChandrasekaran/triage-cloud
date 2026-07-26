"""
Monte Carlo Pi Estimation - CPU Benchmark
Used to compare performance between x86 (t3.micro) and ARM/Graviton (t4g.micro).

How it works: throws random points at a square, checks how many land inside
a circle drawn within it. The ratio of "inside" points approximates Pi.
More points = more accurate, and more CPU work = better benchmark signal.

Usage: python3 benchmark.py
"""

import random
import time

POINTS = 20_000_000  # adjust up/down if the run is too fast/slow to time cleanly


def estimate_pi(num_points):
    inside_circle = 0
    for _ in range(num_points):
        x = random.random()
        y = random.random()
        if x * x + y * y <= 1.0:
            inside_circle += 1
    return 4 * inside_circle / num_points


if __name__ == "__main__":
    start = time.time()
    pi_estimate = estimate_pi(POINTS)
    elapsed = time.time() - start

    print(f"Points used: {POINTS:,}")
    print(f"Pi estimate: {pi_estimate}")
    print(f"Time taken: {elapsed:.2f} seconds")
