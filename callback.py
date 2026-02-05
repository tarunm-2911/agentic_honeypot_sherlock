import requests
from concurrent.futures import ThreadPoolExecutor
from config import FINAL_CALLBACK_URL

# -------------------------------------------------
# THREAD POOL (non-blocking + fast)
# -------------------------------------------------
_executor = ThreadPoolExecutor(max_workers=2)

_timeout = (2, 3)  # connect, read


# -------------------------------------------------
# INTERNAL SENDER
# -------------------------------------------------
def _post_callback(payload):
    try:
        requests.post(
            FINAL_CALLBACK_URL,
            json=payload,
            timeout=_timeout
        )
    except Exception:
        pass  # never block / never crash API


# -------------------------------------------------
# PUBLIC FUNCTION
# -------------------------------------------------
def send_final_callback(session):
    payload = {
        "sessionId": session["sessionId"],
        "scamDetected": True,
        "totalMessagesExchanged": session["message_count"],
        "extractedIntelligence": session["intelligence"],
        "agentNotes": session.get(
            "agent_notes",
            "Scammer used urgency and payment redirection tactics"
        )
    }

    # fire-and-forget (async background)
    _executor.submit(_post_callback, payload)
