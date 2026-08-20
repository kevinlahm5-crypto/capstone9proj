import boto3

ec2 = boto3.client("ec2")
QUARANTINE_SG = "sg-00a41e69d19fc34cb"

def lambda_handler(event, context):
    instance_id = event.get("instanceId")

    if not instance_id:
        event["isolationStatus"] = "SKIPPED_NO_INSTANCE_ID"
        return event

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
    return event
