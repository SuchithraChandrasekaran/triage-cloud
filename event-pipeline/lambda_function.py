"""
triage-cloud-decision-engine

Day 13 update: now reads the project's budget row from DynamoDB when an
event comes in. Real decision logic (approve/block/downgrade) still comes
later, around Day 26 - today just proves Lambda can talk to the table.
"""

import json
import logging
import boto3
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("triage-cloud-budget-tracking")


def decimal_default(obj):
    # DynamoDB returns numbers as Decimal, which json.dumps can't handle directly
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    for record in event.get("Records", []):
        sns_message = record.get("Sns", {}).get("Message", "")
        logger.info("SNS message content: %s", sns_message)

    # Read the triage-cloud project's budget row
    try:
        response = table.get_item(Key={"project_name": "triage-cloud"})
        item = response.get("Item")
        if item:
            logger.info("Budget row found: %s", json.dumps(item, default=decimal_default))
        else:
            logger.info("No budget row found for project_name=triage-cloud")
    except Exception as e:
        logger.error("Error reading DynamoDB table: %s", str(e))

    return {
        "statusCode": 200,
        "body": json.dumps("Event received, logged, and DynamoDB row checked")
    }
