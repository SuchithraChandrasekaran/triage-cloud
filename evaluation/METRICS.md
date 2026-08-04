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
