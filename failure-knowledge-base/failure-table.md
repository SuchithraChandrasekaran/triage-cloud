# Failure Knowledge Base — Table (Day 16)

| failure_type | cause | resource_affected |
|---|---|---|
| IAM misconfiguration | role missing a permission (e.g. s3:PutObject, ssm:GetParameter, logs:CreateLogGroup) | pipeline runs, Lambda writes, EC2 access to secrets/S3 |
| Resource quota exhaustion | vCPU or service limit hit while launching new instances | EC2 launches, new accounts with default 1 vCPU limit |
| Free tier hour depletion | multiple EC2/RDS instances running at once burn the shared 750-hour pool faster | EC2, RDS billing |
| Security group misconfiguration | missing inbound/outbound rule | connections between services, causes timeouts |
| API throttling | automation scripts fire too many AWS API calls at once | ThrottlingException, delayed or failed deployments |
| CloudFormation stack failure | bad parameters, resource conflicts, or missing IAM permissions | stack rolls back, resources not created |
| CodePipeline / CodeBuild failure | wrong artifact path, missing env variables, or bad build config | pipeline stops before deployment triggers |
| CloudWatch logging failure | agent misconfigured or missing IAM permission | no logs or metrics show up, makes debugging harder |
| S3 permission issue | wrong bucket policy or missing IAM role permission | AccessDenied errors, app can't read/write files |
| Disk space exhaustion | batch jobs pile up logs on a small EBS volume | disk fills up, app crashes mid-job |
| Unattached public IP charges | a public IP left attached to a stopped/orphaned resource | keeps billing even though nothing is running |
