import json
import boto3
from datetime import datetime, timezone

s3 = boto3.client("s3")
BUCKET_NAME = "capstone9-guardduty-findings-264787847442"

def lambda_handler(event, context):
    """
    Logs the validated finding to S3 as a timestamped JSON object.
    Expects the output of capstone9-validate-finding as input.
    """
    finding_id = event.get("findingId", "unknown-id")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    key = f"findings/{timestamp}_{finding_id}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(event, indent=2, default=str),
        ContentType="application/json"
    )

    # Pass the original event through, plus where we logged it
    event["s3LogKey"] = key
    return event
