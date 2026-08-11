"""
triage-cloud-decision-engine

Full current version: budget check, dual keyword+AI failure matching
(with negation guard and confidence scoring), agentic investigation
layer, and three-outcome decision (APPROVE / FLAG / BLOCK).

This is the authoritative version - paste this into BOTH the AWS Lambda
console AND the local repo file, so both start identical.
Adds an AI-based (Gemini) semantic failure-pattern check alongside the
existing keyword-based check, so both can be compared honestly.
"""

import json
import logging
import os
import urllib.request
import urllib.error
import boto3
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
budget_table = dynamodb.Table("triage-cloud-budget-tracking")
failure_table = dynamodb.Table("triage-cloud-failure-modes")
review_table = dynamodb.Table("triage-cloud-review-queue")

context_request_id_holder = {"value": "unknown"}

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

if GROQ_API_KEY:
    logger.info("GROQ_API_KEY loaded - length: %d, starts: %s, ends: %s",
                len(GROQ_API_KEY), GROQ_API_KEY[:6], GROQ_API_KEY[-4:])
else:
    logger.info("GROQ_API_KEY is not set")


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


def get_all_failure_rows():
    try:
        response = failure_table.scan()
        return response.get("Items", [])
    except Exception as e:
        logger.error("Error scanning failure table: %s", str(e))
        return []


def check_failure_pattern_keyword(message_text, rows):
    """
    Keyword-based check. Includes a guard against negation/resolved-state
    framing: if the message contains words indicating the issue is past,
    resolved, or explicitly absent, skip the match rather than block a
    safe deployment (fixes a real false positive found during testing).
    """
    message_lower = message_text.lower()

    resolved_or_negation_signals = [
        "resolved", "fixed", "no issue", "no issues", "not found",
        "issues found", "successfully", "completed", "no longer",
        "was fixed", "has been fixed", "review completed"
    ]
    if any(signal in message_lower for signal in resolved_or_negation_signals):
        return None

    for row in rows:
        failure_type = row.get("failure_type", "")
        resource_affected = row.get("resource_affected", "")
        cause = row.get("cause", "")
        cause_phrases = [p.strip().lower() for p in cause.split(",") if p.strip()]
        if (failure_type.lower() in message_lower
                or resource_affected.lower() in message_lower
                or any(phrase in message_lower for phrase in cause_phrases)):
            return failure_type
    return None


def check_failure_pattern_ai(message_text, rows):
    """
    Semantic check using Groq (Llama 3.1 8B, OpenAI-compatible API).
    Returns a (match, confidence) tuple. Returns (None, 0) if the API key
    isn't set or the call fails - this check is additive, never crashes
    the pipeline on its own failure.
    """
    if not GROQ_API_KEY:
        logger.info("AI CHECK: skipped - no GROQ_API_KEY set")
        return None, 0
    New: semantic check using Groq (Llama model, OpenAI-compatible API).
    Sends the message plus the list of known failure types to Groq, asks
    it to pick the best match or 'none'. Returns None if the API key isn't
    set or the call fails - this check is additive, never blocks the
    pipeline on its own failure.
    """
    if not GROQ_API_KEY:
        logger.info("AI CHECK: skipped - no GROQ_API_KEY set")
        return None

    failure_list_text = "\n".join(
        f"- {row.get('failure_type', '')}: {row.get('cause', '')}" for row in rows
    )

    prompt = (
        "You are checking if a deployment message describes an ACTIVE, "
        "CURRENT problem matching a known failure pattern. Here is the "
        "list of known failure types and their causes:\n\n"
        f"{failure_list_text}\n\n"
        f"Message: \"{message_text}\"\n\n"
        "Important: if the message describes an issue that was already "
        "resolved, fixed, or explicitly states no such issue was found "
        "(e.g. past tense, 'no issues', 'successfully resolved', 'review "
        "completed with no problems'), that does NOT count as a match, "
        "even if it mentions the same words - only an active, current "
        "problem counts.\n\n"
        "Reply in exactly this format, two lines:\n"
        "MATCH: <exact failure_type name, or NONE>\n"
        "CONFIDENCE: <a number from 0 to 100, how sure you are>"
        "Reply with ONLY the exact failure_type name if the message "
        "describes an active match to one of the listed patterns (even if "
        "worded differently), or reply with exactly the word NONE if it "
        "doesn't, or if the issue is resolved/negated. No other text."
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    try:
        req = urllib.request.Request(
            GROQ_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "User-Agent": "triage-cloud-lambda/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"].strip()

            match_line = next((l for l in text.split("\n") if l.startswith("MATCH:")), "")
            confidence_line = next((l for l in text.split("\n") if l.startswith("CONFIDENCE:")), "")

            match_value = match_line.replace("MATCH:", "").strip()
            try:
                confidence_value = int("".join(c for c in confidence_line if c.isdigit()))
            except ValueError:
                confidence_value = 0

            logger.info("AI CHECK raw - match: %s, confidence: %d", match_value, confidence_value)

            if match_value.upper() == "NONE" or not match_value:
                return None, confidence_value
            return match_value, confidence_value
    except urllib.error.URLError as e:
        logger.error("Groq API error: %s", str(e))
        return None, 0
    except Exception as e:
        logger.error("Error parsing Groq response: %s", str(e))
        return None, 0
            if text.upper() == "NONE":
                return None
            return text
    except urllib.error.URLError as e:
        logger.error("Groq API error: %s", str(e))
        return None
    except Exception as e:
        logger.error("Error parsing Groq response: %s", str(e))
        return None


def check_architecture_fit(message_text):
    message_lower = message_text.lower()
    if ("fast" in message_lower or "urgent" in message_lower or "priority" in message_lower
            or "quickly" in message_lower or "time-sensitive" in message_lower
            or "asap" in message_lower or "immediately" in message_lower):
        return "x86 (t3.micro) - speed prioritized"
    return "ARM (t4g.micro) - cost prioritized, default"


def investigate_unmatched_case(message_text, rows):
    """
    Agentic step: runs only when neither the keyword check nor the
    semantic check found a match. The agent decides on its own whether
    this looks like a genuinely new, unknown failure pattern worth
    flagging for human review - and if so, takes the action of writing
    it to a review queue table itself, with its own reasoning.
    flagging - and if so, takes the action of writing it to a review
    queue table itself, with its own reasoning. This is a decision +
    action taken by the AI, not a fixed classification returned to a
    human-coded branch.
    """
    if not GROQ_API_KEY:
        return None

    known_types = ", ".join(row.get("failure_type", "") for row in rows)

    prompt = (
        "You are an autonomous monitoring agent for a cloud deployment "
        "system. A message did not match any of the following known "
        "failure patterns:\n"
        f"{known_types}\n\n"
        f"Message: \"{message_text}\"\n\n"
        "Decide: does this message describe a plausible NEW failure "
        "pattern that isn't in the known list, and is worth flagging for "
        "human review? Or is it a normal, non-failure message that "
        "doesn't need flagging?\n\n"
        "Reply in exactly this format, two lines:\n"
        "DECISION: FLAG or DECISION: IGNORE\n"
        "REASON: <one short sentence>"
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    try:
        req = urllib.request.Request(
            GROQ_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "User-Agent": "triage-cloud-lambda/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"].strip()

        decision_line = next((l for l in text.split("\n") if l.startswith("DECISION:")), "")
        reason_line = next((l for l in text.split("\n") if l.startswith("REASON:")), "")

        if "FLAG" in decision_line.upper():
            reason = reason_line.replace("REASON:", "").strip()
            # The agent takes its own action here: writing to the review queue
            try:
                review_table.put_item(Item={
                    "message_id": context_request_id_holder["value"],
                    "message_text": message_text,
                    "agent_reason": reason,
                    "status": "pending_review"
                })
                logger.info("AGENT ACTION: flagged new candidate failure pattern - %s", reason)
                return reason
            except Exception as e:
                logger.error("Agent failed to write to review queue: %s", str(e))
                return None
        else:
            logger.info("AGENT ACTION: reviewed and ignored - not a novel failure pattern")
            return None

    except Exception as e:
        logger.error("Investigation agent error: %s", str(e))
        return None


def make_decision(budget_result, failure_match_keyword, failure_match_ai, agent_flag, architecture_suggestion):
    if budget_result["status"] == "over":
        return "BLOCK - project is over budget"
    # Either check catching a match is enough to block
    final_match = failure_match_keyword or failure_match_ai
    if final_match:
        return f"BLOCK - matches known failure pattern: {final_match}"
    if agent_flag:
        return f"FLAG - agent identified a possible new failure pattern: {agent_flag}"
    return f"APPROVE - suggested instance: {architecture_suggestion}"


def lambda_handler(event, context):
    context_request_id_holder["value"] = getattr(context, "aws_request_id", "unknown")
    logger.info("Received event: %s", json.dumps(event))

    sns_message = ""
    for record in event.get("Records", []):
        sns_message = record.get("Sns", {}).get("Message", "")
        logger.info("SNS message content: %s", sns_message)

    budget_result = check_budget("triage-cloud")
    logger.info("BUDGET CHECK: %s", json.dumps(budget_result, default=decimal_default))

    failure_rows = get_all_failure_rows()

    failure_match_keyword = check_failure_pattern_keyword(sns_message, failure_rows)
    logger.info("FAILURE CHECK (keyword): %s", failure_match_keyword if failure_match_keyword else "no match found")

    failure_match_ai, ai_confidence = check_failure_pattern_ai(sns_message, failure_rows)
    logger.info("FAILURE CHECK (AI): %s (confidence: %d)",
                failure_match_ai if failure_match_ai else "no match found", ai_confidence)
    failure_match_ai = check_failure_pattern_ai(sns_message, failure_rows)
    logger.info("FAILURE CHECK (AI): %s", failure_match_ai if failure_match_ai else "no match found")

    agent_flag = None
    if not failure_match_keyword and not failure_match_ai:
        agent_flag = investigate_unmatched_case(sns_message, failure_rows)

    architecture_suggestion = check_architecture_fit(sns_message)
    logger.info("ARCHITECTURE CHECK: %s", architecture_suggestion)

    final_decision = make_decision(budget_result, failure_match_keyword, failure_match_ai, agent_flag, architecture_suggestion)
    logger.info("DECISION: %s", final_decision)

    return {
        "statusCode": 200,
        "body": json.dumps({"decision": final_decision})
    }
