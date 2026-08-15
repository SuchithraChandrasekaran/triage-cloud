# Chaos/Stress Testing Log

Testing malformed and edge-case inputs to see where the system actually
breaks, documented honestly regardless of outcome.

## Test 1: Truncated/malformed JSON-like string
Input: `{"incomplete": "json`

Result: No crash. Keyword and AI checks both correctly found no match.
The agentic layer correctly identified the message as JSON-parsing-error
shaped and FLAGGED it for review, with reasoning: "The message indicates
a parsing error, suggesting a potential issue with the system's ability
to process or handle JSON data." This is a genuinely good outcome - the
system degraded gracefully and the agent's judgment was sound, not a
false alarm.

## Test 2: Empty/blank message
Input: `""`

Result: A real, more serious bug found. Groq did not follow the expected
MATCH:/CONFIDENCE: response format for an empty input - it replied
conversationally ("Please provide the deployment message. I'll check for
a match."). The parsing code had no validation that the returned match
value is an actual known failure_type, so it treated the AI's confused
reply as a valid match and BLOCKED the deployment citing a
non-existent "failure pattern" (the AI's own sentence). This is a real
robustness gap: the system trusted the AI's output shape without
verifying it against the known failure list.

**Fix applied:** added validation so a match is only accepted if it
exactly matches one of the real failure_type values passed to the model,
not any arbitrary text the model returns.

**Re-test after fix:** Empty message no longer causes a bogus BLOCK. AI
check correctly discards the invalid response ("AI CHECK raw - match: ,
confidence: 0"), falls through cleanly, and the agentic layer correctly
flags the empty message itself as worth human review - a sound, honest
judgment call rather than a false BLOCK or a silent APPROVE.

## Test 3: Massive payload (large, multi-thousand-character repeated text)
Input: A large, multi-thousand-character message of repeated filler text.

Result: No crash, no timeout. Keyword check ran normally. AI check
correctly returned NONE with high confidence (100) - no false match on
the repetition alone. The agentic layer independently identified the
repeating pattern itself as unusual and FLAGGED it for review ("contains
a repeating pattern of text that could indicate a potential issue with
the system's behavior or performance"). System handled a payload roughly
100x larger than typical test messages without degradation.

## Test 4: Unicode and emoji
Input: `🚀💥 Deployment 失败 emoji test ñ ü é 中文 problem`

Result: No crash, no encoding errors. Keyword check found no match (as
expected, none of the English failure-mode terms are present). AI check
correctly evaluated the full multilingual content and returned NONE with
confidence 0. The agentic layer went further and correctly recognized
the Chinese text "失败" (meaning "failure") as a genuine deployment
failure indicator, and appropriately flagged the message alongside noting
the internationalization/encoding angle. This demonstrates the AI layer's
semantic understanding extends across languages, not just English
keyword-adjacent phrasing.

## Test 5: Whitespace-only message
Input: `"     "` (five spaces, no other content)

Result: Behaved identically to the empty-string case (Test 2, post-fix).
No crash. AI check correctly discarded (empty raw match), agentic layer
flagged the message as empty/unusual, worth review. Confirms the earlier
validation fix generalizes to whitespace-only input, not just a literal
empty string.

## Chaos Testing Summary

Five deliberately malformed or unusual inputs were tested: truncated
JSON-like text, an empty string, a large, multi-thousand-character repeated payload,
mixed Unicode/emoji/multilingual text, and a whitespace-only string. The
system did not crash or time out on any of them. One real, more serious
bug was found and fixed: an empty message caused Groq to reply
conversationally instead of following the expected format, and the
parsing code had no validation that the returned match was an actual
known failure type - this caused a bogus BLOCK on a non-existent failure
pattern. A validation check was added so only genuine, known failure
types can trigger a block, regardless of what text the AI returns. After
the fix, all five chaos cases degraded gracefully, most resulting in the
agentic layer correctly and independently flagging the unusual input for
human review rather than silently approving or incorrectly blocking it.
