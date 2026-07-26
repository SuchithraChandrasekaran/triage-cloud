# Failure Modes — Day 3 notes

1. **IAM misconfiguration** — role missing a permission (e.g. `s3:PutObject`, `ssm:GetParameter`,
   `logs:CreateLogGroup`) — blocks pipeline runs, Lambda writes, or EC2 access to secrets/S3.

2. **Resource quota exhaustion** — vCPU or service limit hit while launching new instances —
   stops EC2 launches mid-migration, common on new/free-tier accounts (default 1 vCPU limit).

3. **Free tier hour depletion** — running multiple EC2/RDS instances at once burns through the
   shared 750-hour monthly pool faster than expected — instances start incurring charges.

4. **API throttling** — automation scripts fire too many AWS API calls at once — causes
   `ThrottlingException`, delayed or failed deployments.

5. **CloudFormation stack failure** — bad parameters, resource conflicts, or missing IAM perms —
   stack rolls back, nothing gets created.

6. **CodePipeline / CodeBuild failure** — wrong artifact path, missing env variables, or bad
   build config — pipeline stops before deployment triggers.

7. **CloudWatch logging failure** — agent misconfigured or missing IAM permission — no logs or
   metrics show up, makes every other failure harder to debug.

8. **S3 permission issue** — wrong bucket policy or missing IAM role permission — app can't
   read/write files, `AccessDenied` errors.

9. **Security group / network misconfiguration** — missing inbound/outbound rule — connection
   timeouts, services can't talk to each other.

10. **Disk space exhaustion** — batch jobs pile up logs on a small EBS volume — disk fills up,
    app crashes mid-job.

11. **Unattached public IP charges** — a public IP left attached to a stopped/orphaned resource —
    keeps billing even though nothing is running.

## Most relevant to this project
Since triage-cloud is meant to catch failures *before* deployment, the ones worth prioritizing
in the knowledge base are the ones that are predictable from the request itself, before
anything runs: IAM misconfiguration, quota exhaustion, free tier depletion, and security group
misconfiguration. These four can realistically be checked against a request (role, region,
instance type, account state) without needing live telemetry.
