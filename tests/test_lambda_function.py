"""
Unit tests for investigate_unmatched_case() (mocks Groq + the review
queue table) and an integration test for lambda_handler() end-to-end
(mocks everything: SNS event shape, DynamoDB, Groq) - the final piece
of full coverage for this module.
"""

import sys
import os
import json
from unittest.mock import patch, MagicMock

import lambda_function
# Adjust this path to point at your event-pipeline folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "event-pipeline"))

from lambda_function import check_architecture_fit


def test_urgent_keyword_suggests_x86():
    result = check_architecture_fit("Urgent deployment needed")
    assert "x86" in result


def test_fast_keyword_suggests_x86():
    result = check_architecture_fit("Fast turnaround required")
    assert "x86" in result


def test_priority_keyword_suggests_x86():
    result = check_architecture_fit("Priority release for triage-cloud")
    assert "x86" in result


def test_quickly_keyword_suggests_x86():
    result = check_architecture_fit("Deploy this as quickly as possible")
    assert "x86" in result


def test_no_urgency_signal_defaults_to_arm():
    result = check_architecture_fit("Routine batch job for triage-cloud")
    assert "ARM" in result


def test_empty_message_defaults_to_arm():
    result = check_architecture_fit("")
    assert "ARM" in result


def test_case_insensitivity():
    result = check_architecture_fit("URGENT DEPLOYMENT NEEDED")
    assert "x86" in result
"""
Unit tests for check_failure_pattern_keyword() - pure logic, no AWS calls.
Uses fake 'rows' data instead of real DynamoDB, so this runs fast and free.
"""

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "event-pipeline"))

from lambda_function import check_failure_pattern_keyword


FAKE_ROWS = [
    {
        "failure_type": "IAM misconfiguration",
        "cause": "role missing a permission, wrong trust relationship",
        "resource_affected": "pipeline runs, Lambda writes"
    },
    {
        "failure_type": "Resource quota exhaustion",
        "cause": "vCPU or service limit hit, quota exceeded",
        "resource_affected": "EC2 launches"
    },
    {
        "failure_type": "Security group misconfiguration",
        "cause": "missing inbound/outbound rule, blocking required traffic",
        "resource_affected": "connections between services"
    },
]


def test_matches_failure_type_directly():
    result = check_failure_pattern_keyword("IAM misconfiguration detected", FAKE_ROWS)
    assert result == "IAM misconfiguration"


def test_matches_via_cause_phrase():
    result = check_failure_pattern_keyword("vCPU or service limit hit while launching", FAKE_ROWS)
    assert result == "Resource quota exhaustion"


def test_matches_via_split_cause_phrase():
    # tests the Day 32 fix: comma-separated phrases checked individually
    result = check_failure_pattern_keyword("Security group blocking required traffic", FAKE_ROWS)
    assert result == "Security group misconfiguration"


def test_no_match_for_unrelated_message():
    result = check_failure_pattern_keyword("Routine deployment check", FAKE_ROWS)
    assert result is None


def test_negation_guard_blocks_resolved_language():
    result = check_failure_pattern_keyword(
        "We successfully resolved the IAM misconfiguration issue yesterday", FAKE_ROWS
    )
    assert result is None


def test_negation_guard_blocks_no_issues_language():
    result = check_failure_pattern_keyword(
        "Quota review completed, no issues found", FAKE_ROWS
    )
    assert result is None


def test_empty_rows_returns_none():
    result = check_failure_pattern_keyword("IAM misconfiguration detected", [])
    assert result is None
"""
Unit tests for make_decision() - the core orchestration logic. Pure
function, no AWS/Groq calls, so no mocking needed. Tests the priority
order: budget blocks first, then failure match, then flag, then approve.
"""

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "event-pipeline"))

from lambda_function import make_decision


def test_over_budget_blocks_regardless_of_other_signals():
    budget_result = {"status": "over", "current_spend": 10, "budget_limit": 5}
    result = make_decision(budget_result, None, None, None, "ARM (t4g.micro)")
    assert result.startswith("BLOCK - project is over budget")


def test_over_budget_blocks_even_if_failure_also_matched():
    # budget check should win even when a failure pattern also matched -
    # tests the priority order, not just each branch in isolation
    budget_result = {"status": "over", "current_spend": 10, "budget_limit": 5}
    result = make_decision(budget_result, "IAM misconfiguration", None, None, "ARM")
    assert "over budget" in result
    assert "IAM misconfiguration" not in result


def test_keyword_failure_match_blocks():
    budget_result = {"status": "ok", "current_spend": 0, "budget_limit": 10}
    result = make_decision(budget_result, "IAM misconfiguration", None, None, "ARM")
    assert result == "BLOCK - matches known failure pattern: IAM misconfiguration"


def test_ai_failure_match_blocks():
    budget_result = {"status": "ok", "current_spend": 0, "budget_limit": 10}
    result = make_decision(budget_result, None, "Security group misconfiguration", None, "ARM")
    assert result == "BLOCK - matches known failure pattern: Security group misconfiguration"


def test_keyword_match_takes_priority_when_both_check_agree():
    budget_result = {"status": "ok", "current_spend": 0, "budget_limit": 10}
    result = make_decision(budget_result, "IAM misconfiguration", "IAM misconfiguration", None, "ARM")
    assert result == "BLOCK - matches known failure pattern: IAM misconfiguration"


def test_agent_flag_when_no_other_match():
    budget_result = {"status": "ok", "current_spend": 0, "budget_limit": 10}
    result = make_decision(budget_result, None, None, "possible new pattern found", "ARM")
    assert result.startswith("FLAG")
    assert "possible new pattern found" in result


def test_clean_case_approves_with_architecture_suggestion():
    budget_result = {"status": "ok", "current_spend": 0, "budget_limit": 10}
    result = make_decision(budget_result, None, None, None, "ARM (t4g.micro) - cost prioritized, default")
    assert result == "APPROVE - suggested instance: ARM (t4g.micro) - cost prioritized, default"


def test_failure_match_takes_priority_over_agent_flag():
    # if a failure matched, the agent shouldn't even matter - block wins
    budget_result = {"status": "ok", "current_spend": 0, "budget_limit": 10}
    result = make_decision(budget_result, "IAM misconfiguration", None, "some flag text", "ARM")
    assert result.startswith("BLOCK")
"""
Unit tests for check_budget(). This function calls real DynamoDB, so we
mock the table's get_item response using unittest.mock - no AWS
credentials, no network calls, no cost, and the test runs in milliseconds
instead of waiting on a real API round-trip.
"""

from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "event-pipeline"))

import lambda_function


def test_within_budget_returns_ok():
    fake_response = {
        "Item": {"project_name": "triage-cloud", "current_spend": 1, "budget_limit": 10}
    }
    with patch.object(lambda_function.budget_table, "get_item", return_value=fake_response):
        result = lambda_function.check_budget("triage-cloud")
    assert result["status"] == "ok"
    assert result["current_spend"] == 1.0
    assert result["budget_limit"] == 10.0


def test_over_budget_returns_over():
    fake_response = {
        "Item": {"project_name": "triage-cloud", "current_spend": 15, "budget_limit": 10}
    }
    with patch.object(lambda_function.budget_table, "get_item", return_value=fake_response):
        result = lambda_function.check_budget("triage-cloud")
    assert result["status"] == "over"


def test_spend_equal_to_limit_is_not_over():
    # boundary case tested manually on Day 32/extended - strict > comparison
    fake_response = {
        "Item": {"project_name": "triage-cloud", "current_spend": 5, "budget_limit": 5}
    }
    with patch.object(lambda_function.budget_table, "get_item", return_value=fake_response):
        result = lambda_function.check_budget("triage-cloud")
    assert result["status"] == "ok"


def test_missing_project_returns_unknown():
    fake_response = {}  # no "Item" key - project not found in table
    with patch.object(lambda_function.budget_table, "get_item", return_value=fake_response):
        result = lambda_function.check_budget("nonexistent-project")
    assert result["status"] == "unknown"


def test_dynamodb_error_returns_error_status():
    with patch.object(lambda_function.budget_table, "get_item", side_effect=Exception("boto3 error")):
        result = lambda_function.check_budget("triage-cloud")
    assert result["status"] == "error"
"""
Unit tests for check_failure_pattern_ai(). This function calls the real
Groq API, so we mock urllib.request.urlopen's response - no real network
call, no API cost, no dependency on Groq being up.
"""

import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "event-pipeline"))



def make_fake_groq_response(content_text):
    """Builds a fake response object shaped like what urlopen returns."""
    fake_body = json.dumps({
        "choices": [{"message": {"content": content_text}}]
    }).encode("utf-8")

    fake_response = MagicMock()
    fake_response.read.return_value = fake_body
    fake_response.__enter__.return_value = fake_response
    fake_response.__exit__.return_value = False
    return fake_response


def test_ai_finds_a_match_with_confidence():
    fake_content = "MATCH: IAM misconfiguration\nCONFIDENCE: 90"
    with patch.object(lambda_function, "GROQ_API_KEY", "fake-key-for-testing"):
        with patch("urllib.request.urlopen", return_value=make_fake_groq_response(fake_content)):
            match, confidence = lambda_function.check_failure_pattern_ai("some message", [])
    assert match == "IAM misconfiguration"
    assert confidence == 90


def test_ai_returns_none_for_no_match():
    fake_content = "MATCH: NONE\nCONFIDENCE: 80"
    with patch.object(lambda_function, "GROQ_API_KEY", "fake-key-for-testing"):
        with patch("urllib.request.urlopen", return_value=make_fake_groq_response(fake_content)):
            match, confidence = lambda_function.check_failure_pattern_ai("safe message", [])
    assert match is None
    assert confidence == 80


def test_missing_api_key_skips_check():
    with patch.object(lambda_function, "GROQ_API_KEY", None):
        match, confidence = lambda_function.check_failure_pattern_ai("any message", [])
    assert match is None
    assert confidence == 0


def test_api_error_returns_none_gracefully():
    # simulates the real 403/429 errors hit during development - the
    # function should degrade gracefully, not crash the whole pipeline
    import urllib.error
    with patch.object(lambda_function, "GROQ_API_KEY", "fake-key-for-testing"):
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("simulated failure")):
            match, confidence = lambda_function.check_failure_pattern_ai("some message", [])
    assert match is None
    assert confidence == 0


def test_malformed_response_does_not_crash():
    fake_content = "this is not the expected format at all"
    with patch.object(lambda_function, "GROQ_API_KEY", "fake-key-for-testing"):
        with patch("urllib.request.urlopen", return_value=make_fake_groq_response(fake_content)):
            match, confidence = lambda_function.check_failure_pattern_ai("some message", [])
    assert match is None
    assert confidence == 0

def make_fake_groq_response(content_text):
    fake_body = json.dumps({
        "choices": [{"message": {"content": content_text}}]
    }).encode("utf-8")
    fake_response = MagicMock()
    fake_response.read.return_value = fake_body
    fake_response.__enter__.return_value = fake_response
    fake_response.__exit__.return_value = False
    return fake_response


# ---------- investigate_unmatched_case ----------

def test_agent_flags_novel_pattern_and_writes_to_review_table():
    fake_content = "DECISION: FLAG\nREASON: Deployment stuck with no clear cause"
    with patch.object(lambda_function, "GROQ_API_KEY", "fake-key"):
        with patch("urllib.request.urlopen", return_value=make_fake_groq_response(fake_content)):
            with patch.object(lambda_function.review_table, "put_item") as mock_put:
                result = lambda_function.investigate_unmatched_case("stuck deployment", [])
    assert result == "Deployment stuck with no clear cause"
    mock_put.assert_called_once()


def test_agent_ignores_normal_message():
    fake_content = "DECISION: IGNORE\nREASON: Normal routine message"
    with patch.object(lambda_function, "GROQ_API_KEY", "fake-key"):
        with patch("urllib.request.urlopen", return_value=make_fake_groq_response(fake_content)):
            with patch.object(lambda_function.review_table, "put_item") as mock_put:
                result = lambda_function.investigate_unmatched_case("routine message", [])
    assert result is None
    mock_put.assert_not_called()


def test_agent_returns_none_when_no_api_key():
    with patch.object(lambda_function, "GROQ_API_KEY", None):
        result = lambda_function.investigate_unmatched_case("any message", [])
    assert result is None


def test_agent_handles_review_table_write_failure_gracefully():
    fake_content = "DECISION: FLAG\nREASON: Something new"
    with patch.object(lambda_function, "GROQ_API_KEY", "fake-key"):
        with patch("urllib.request.urlopen", return_value=make_fake_groq_response(fake_content)):
            with patch.object(lambda_function.review_table, "put_item", side_effect=Exception("write failed")):
                result = lambda_function.investigate_unmatched_case("some message", [])
    assert result is None  # should not crash, just return None on write failure


# ---------- lambda_handler (full integration) ----------

def make_sns_event(message_text):
    return {
        "Records": [
            {"EventSource": "aws:sns", "Sns": {"Message": message_text, "Subject": "AWS Budget Alert"}}
        ]
    }


def test_handler_approves_clean_case_end_to_end():
    fake_context = MagicMock()
    fake_context.aws_request_id = "test-request-id"

    with patch.object(lambda_function.budget_table, "get_item",
                       return_value={"Item": {"project_name": "triage-cloud", "current_spend": 0, "budget_limit": 10}}):
        with patch.object(lambda_function.failure_table, "scan", return_value={"Items": []}):
            with patch.object(lambda_function, "GROQ_API_KEY", None):  # AI checks skipped
                result = lambda_function.lambda_handler(make_sns_event("Routine deployment check"), fake_context)

    body = json.loads(result["body"])
    assert body["decision"].startswith("APPROVE")
    assert result["statusCode"] == 200


def test_handler_blocks_over_budget_end_to_end():
    fake_context = MagicMock()
    fake_context.aws_request_id = "test-request-id"

    with patch.object(lambda_function.budget_table, "get_item",
                       return_value={"Item": {"project_name": "triage-cloud", "current_spend": 20, "budget_limit": 10}}):
        with patch.object(lambda_function.failure_table, "scan", return_value={"Items": []}):
            with patch.object(lambda_function, "GROQ_API_KEY", None):
                result = lambda_function.lambda_handler(make_sns_event("Routine deployment check"), fake_context)

    body = json.loads(result["body"])
    assert body["decision"].startswith("BLOCK - project is over budget")


def test_handler_blocks_known_failure_pattern_end_to_end():
    fake_context = MagicMock()
    fake_context.aws_request_id = "test-request-id"

    fake_rows = [{"failure_type": "IAM misconfiguration", "cause": "role missing a permission", "resource_affected": "pipeline runs"}]

    with patch.object(lambda_function.budget_table, "get_item",
                       return_value={"Item": {"project_name": "triage-cloud", "current_spend": 0, "budget_limit": 10}}):
        with patch.object(lambda_function.failure_table, "scan", return_value={"Items": fake_rows}):
            with patch.object(lambda_function, "GROQ_API_KEY", None):
                result = lambda_function.lambda_handler(make_sns_event("IAM misconfiguration detected"), fake_context)

    body = json.loads(result["body"])
    assert "BLOCK" in body["decision"]
    assert "IAM misconfiguration" in body["decision"]
