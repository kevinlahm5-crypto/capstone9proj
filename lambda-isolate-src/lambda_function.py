import boto3
import json
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2")
sns = boto3.client("sns")
QUARANTINE_SG = "sg-00a41e69d19fc34cb"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:264787847442:capstone9-security-alerts"

def lambda_handler(event, context):
    """
    Isolates an EC2 instance by swapping its security group to the
    quarantine SG, then notifies the security team via SNS.
    """
    instance_id = event.get("instanceId")
    finding_type = event.get("findingType", "Unknown")
    severity = event.get("severity", "Unknown")
    finding_id = event.get("findingId", "unknown-id")

    if not instance_id:
        event["isolationStatus"] = "SKIPPED_NO_INSTANCE_ID"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="GuardDuty Alert - No Instance to Isolate",
            Message=f"High severity finding {finding_id} ({finding_type}, severity {severity}) "
                    f"had no associated EC2 instance. No isolation action taken. Manual review required."
        )
        return event

    try:
        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[QUARANTINE_SG]
        )
        ec2.create_tags(
            Resources=[instance_id],
            Tags=[{"Key": "IsolationStatus", "Value": "Quarantined-AutoResponse"}]
        )
        event["isolationStatus"] = "ISOLATED"
        event["quarantineSecurityGroup"] = QUARANTINE_SG
        isolation_note = f"The instance has been moved to a security group with no inbound or outbound rules."
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidInstanceID.NotFound":
            event["isolationStatus"] = "SKIPPED_TEST_INSTANCE_NOT_FOUND"
            isolation_note = (
                f"Instance {instance_id} does not exist (likely a GuardDuty sample/test finding). "
                f"No real isolation action was needed."
            )
        else:
            raise

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"GuardDuty Incident Response - Instance {instance_id}",
        Message=(
            f"Automated incident response completed.\n\n"
            f"Finding ID: {finding_id}\n"
            f"Finding Type: {finding_type}\n"
            f"Severity: {severity}\n"
            f"Instance: {instance_id}\n"
            f"Status: {event['isolationStatus']}\n\n"
            f"{isolation_note}"
        )
    )

    return event
