# Problem Statement

## 1. Cost alerts are reactive, not preventive
Cloud cost tools like AWS Budgets and Cost Anomaly Detection notify teams
after spending has already happened. Nothing in the deployment pipeline
itself checks budget status before a resource is provisioned — the alert
arrives, but the infrastructure is already running.

## 2. Deployment failures repeat because history isn't checked
Known failure patterns (quota exhaustion, IAM misconfiguration, throttling)
recur across teams and projects. Postmortems document them, but that
knowledge rarely feeds back into the deployment process itself — each new
deployment starts blind to failures that already happened before.

## 3. Architecture choices are rarely backed by live cost/performance data
Instance type selection (e.g., ARM vs x86) is often based on habit or
default choice rather than measured cost-to-performance data for the
specific workload being deployed.

## The gap
No existing framework checks all three signals — budget, failure risk,
and architecture fit — at the moment of deployment, before infrastructure
is provisioned. Cost governance, failure prevention, and architecture
optimization are handled by separate tools, after the fact, instead of
as one decision made before provisioning.
