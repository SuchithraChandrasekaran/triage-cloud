"""
triage-cloud-decision-engine

Day 18 update: added a failure-pattern check. Scans the
triage-cloud-failure-modes table and checks if the incoming message
mentions any known failure type or affected resource.
"""

import json
import logging
import boto3
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
budget_table = dynamodb.Table("triage-cloud-budget-tracking")
failure_table = dynamodb.Table("triage-cloud-failure-modes")


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def check_failure_pattern(message_text):
    """
    Very simple keyword match for now: checks if any known failure_type
    or resource_affected text appears in the incoming message.
    Good enough to prove the check works - can be made smarter later.
    """
    try:
        response = failure_table.scan()
        rows = response.get("Items", [])
    except Exception as e:
        logger.error("Error scanning failure table: %s", str(e))
        return None

    message_lower = message_text.lower()
    for row in rows:
        failure_type = row.get("failure_type", "")
        resource_affected = row.get("resource_affected", "")
        if failure_type.lower() in message_lower or resource_affected.lower() in message_lower:
            return failure_type

    return None


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    sns_message = ""
    for record in event.get("Records", []):
        sns_message = record.get("Sns", {}).get("Message", "")
        logger.info("SNS message content: %s", sns_message)

    # Read the triage-cloud project's budget row
    item = None
    try:
        response = budget_table.get_item(Key={"project_name": "triage-cloud"})
        item = response.get("Item")
        if item:
            logger.info("Budget row found: %s", json.dumps(item, default=decimal_default))
        else:
            logger.info("No budget row found for project_name=triage-cloud")
    except Exception as e:
        logger.error("Error reading DynamoDB table: %s", str(e))

    # Check the message against known failure patterns
    matched_failure = check_failure_pattern(sns_message)
    if matched_failure:
        logger.info("FAILURE CHECK: matched %s", matched_failure)
    else:
        logger.info("FAILURE CHECK: no match found")

    logger.info(
        "DECISION: no rule applied yet - budget=%s, failure_check=%s, architecture_check=pending",
        item.get("current_spend") if item else "unknown",
        matched_failure if matched_failure else "clear"
    )

    return {
        "statusCode": 200,
        "body": json.dumps("Event received, logged, DynamoDB checked, failure pattern checked")
    }
