import time

_sessions = {}


def get_session(session_id: str):

    if session_id not in _sessions:
        _sessions[session_id] = {
            "sessionId": session_id,
            "start_time": time.time(),
            "message_count": 0,
            "scamDetected": False,
            "messages": [],
            "agent_notes": "",
            "callback_sent": False,   # ✅ new
            "intelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            }
        }

    return _sessions[session_id]
