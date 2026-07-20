# Related Work — Day 2 notes

1. **Automating FinOps in Cloud Computing (CloudCom 2024)** — Uses LLMs to pull cost data from
   different cloud providers and put it in one standard format. Good at collecting data. Doesn't
   do anything about failures or which instance type to pick, and doesn't stop a deployment
   before it happens.

2. **Improving FinOps Procedures with Automation (Aalto thesis, 2024)** — Tracks resources in
   real time and shuts down unused ones automatically. But it acts after the waste already
   happened, not before. Also a thesis, not a published paper, so lighter weight as a source.

3. **FinOps Agent (arXiv, 2025)** — An AI agent that looks at cost data and suggests what to
   optimize. Still needs a human to read the suggestion and act on it. No failure check, no
   architecture check, no automatic blocking.

4. **Cost-Aware Elastic Cloud Provisioning (IEEE 2015)** — Picks instances based on live spot
   prices, big cost savings (97%). Only looks at cost. Nothing about failure history or ARM vs
   x86 tradeoffs.

5. **Kingfisher (IEEE INFOCOM 2011)** — Older paper, picks server configs to save cost and cut
   reconfiguration time. Same gap — cost only, one signal, not three.

## What's missing across all five
Every paper does one thing: track cost, suggest cost savings, or provision based on cost alone.
None of them check cost + failure risk + architecture fit together, and none of them act
*before* a deployment happens — they all react after the fact. That's the open space this
project is trying to fill.
