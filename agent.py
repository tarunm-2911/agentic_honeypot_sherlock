# -------------------------------------------------
# FAST RULE-BASED FALLBACK AGENT (zero latency)
# -------------------------------------------------

AGENT_RESPONSES = (
    "Which bank is this?",
    "Why is my account blocked?",
    "Can you explain again?",
    "Is this really urgent?",
    "What happens if I don't pay?",
    "How do I verify this?"
)


def generate_agent_reply(message_count: int) -> str:
    idx = message_count % len(AGENT_RESPONSES)
    return AGENT_RESPONSES[idx]
