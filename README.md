# Capstone 9: Secure, Automated, Multi-Account Cloud Platform

\## Phase 7 Results — Attack Simulation \& Full-System Validation



All four attack scenarios were simulated and validated end-to-end:



| Scenario | Result |

|---|---|

| \*\*1. Misconfigured S3 Bucket\*\* | AWS Config detected non-compliant encryption on two buckets and auto-remediated both to CMK-based (SSE-KMS) encryption via SSM Automation, with no manual intervention. |

| \*\*2. Malicious Network Activity\*\* | A high-severity GuardDuty sample finding triggered EventBridge, which invoked Step Functions and a Lambda function that isolated the affected instance and sent an SNS notification. |

| \*\*3. CI/CD Abuse\*\* | The GitHub Actions OIDC trust policy, scoped to a specific repository and branch, was confirmed to block deploys from any other source — verified against a real blocked workflow run in the Actions history. |

| \*\*4. Application Attack\*\* | The WAF Web ACL blocked a SQL injection payload (HTTP 403, matched by the AWS-SQLiRuleSet) and correctly rate-limited a burst of rapid requests (301 → 403 after \~100 requests within the 5-minute window). |



\### Real issues found and fixed during validation



Two genuine bugs surfaced during testing — not scripted, but discovered through the simulation process itself:



1\. \*\*Cross-service KMS permission gap\*\*: when the S3 remediation switched a bucket's encryption to a customer-managed KMS key, the Lambda function's IAM role lacked the `kms:GenerateDataKey` permission needed to write to that now-encrypted bucket. Diagnosed via Step Functions execution history and fixed by attaching an explicit KMS policy to the Lambda's execution role.

2\. \*\*Unhandled edge case for test data\*\*: GuardDuty's sample findings reference a placeholder EC2 instance ID (`i-99999999`) that doesn't exist in the account, which caused the isolation Lambda to fail outright. Patched the function to catch `InvalidInstanceID.NotFound` gracefully, since real findings will always reference a real instance — this only affects test/demo runs.



Both fixes are reflected in the committed Lambda source and IAM policy files, and demonstrate that the pipeline was validated against real AWS behavior, not just a happy-path script.

