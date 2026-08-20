import json

def lambda_handler(event, context):
    """
    Validates an incoming GuardDuty finding.
    Expects the raw GuardDuty finding detail (as passed by EventBridge).
    """
    detail = event.get("detail", event)  # handle both wrapped and raw input

    severity = detail.get("severity", 0)
    finding_type = detail.get("type", "Unknown")
    finding_id = detail.get("id", "unknown-id")
    instance_id = None

    # Try to pull the affected EC2 instance ID out of the finding, if present
    resource = detail.get("resource", {})
    instance_details = resource.get("instanceDetails", {})
    if instance_details:
        instance_id = instance_details.get("instanceId")

    is_valid = severity >= 7.0  # HIGH severity threshold

    return {
        "isValid": is_valid,
        "findingId": finding_id,
        "findingType": finding_type,
        "severity": severity,
        "instanceId": instance_id,
        "rawFinding": detail
    }
