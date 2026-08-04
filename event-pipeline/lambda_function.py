"""
triage-cloud-decision-engine

Day 26 update: added an architecture-fit check and a combined
make_decision() function that pulls together budget, failure risk, and
architecture fit into one final answer.
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


def check_budget(project_name):
    try:
        response = budget_table.get_item(Key={"project_name": project_name})
        item = response.get("Item")
        if not item:
            return {"status": "unknown", "current_spend": None, "budget_limit": None}
        current_spend = float(item.get("current_spend", 0))
        budget_limit = float(item.get("budget_limit", 0))
        over_budget = current_spend > budget_limit
        return {
            "status": "over" if over_budget else "ok",
            "current_spend": current_spend,
            "budget_limit": budget_limit
        }
    except Exception as e:
        logger.error("Error reading budget table: %s", str(e))
        return {"status": "error", "current_spend": None, "budget_limit": None}


def check_failure_pattern(message_text):
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
        cause = row.get("cause", "")
        if (failure_type.lower() in message_lower
                or resource_affected.lower() in message_lower
                or cause.lower() in message_lower):
            return failure_type
    return None


def check_architecture_fit(message_text):
    """
    Simple rule from Day 25: default to ARM (cheaper), unless the message
    signals speed/urgency matters more, then suggest x86.
    """
    message_lower = message_text.lower()
    if "fast" in message_lower or "urgent" in message_lower or "priority" in message_lower:
        return "x86 (t3.micro) - speed prioritized"
    return "ARM (t4g.micro) - cost prioritized, default"


def make_decision(budget_result, failure_match, architecture_suggestion):
    if budget_result["status"] == "over":
        return "BLOCK - project is over budget"
    if failure_match:
        return f"BLOCK - matches known failure pattern: {failure_match}"
    return f"APPROVE - suggested instance: {architecture_suggestion}"


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    sns_message = ""
    for record in event.get("Records", []):
        sns_message = record.get("Sns", {}).get("Message", "")
        logger.info("SNS message content: %s", sns_message)

    budget_result = check_budget("triage-cloud")
    logger.info("BUDGET CHECK: %s", json.dumps(budget_result, default=decimal_default))

    failure_match = check_failure_pattern(sns_message)
    logger.info("FAILURE CHECK: %s", failure_match if failure_match else "no match found")

    architecture_suggestion = check_architecture_fit(sns_message)
    logger.info("ARCHITECTURE CHECK: %s", architecture_suggestion)

    final_decision = make_decision(budget_result, failure_match, architecture_suggestion)
    logger.info("DECISION: %s", final_decision)

    return {
        "statusCode": 200,
        "body": json.dumps({"decision": final_decision})
    }
