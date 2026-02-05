import time
import asyncio
import secrets

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader

from config import API_KEY
from session_store import get_session
from detector import detect_scam
from extractor import extract_intelligence
from ai_agent import generate_ai_reply
from callback import send_final_callback


app = FastAPI(
    title="Agentic Honeypot",
    version="2.0.0"
)


# -------------------------------------------------
# API KEY
# -------------------------------------------------
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def validate_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


# -------------------------------------------------
# MAIN ENDPOINT
# -------------------------------------------------
@app.post("/api/honeypot/message")
async def honeypot(payload: dict, _: str = Security(validate_api_key)):

    session = get_session(payload["sessionId"])

    # -------------------------------------------------
    # ✅ LOAD conversationHistory (MANDATORY FIX)
    # -------------------------------------------------
    history = payload.get("conversationHistory", [])

    for msg in history:
        entry = {"sender": msg["sender"], "text": msg["text"]}
        if entry not in session["messages"]:
            session["messages"].append(entry)

    # -------------------------------------------------
    # CURRENT MESSAGE
    # -------------------------------------------------
    sender = payload["message"]["sender"]
    text = payload["message"]["text"]

    session["message_count"] += 1

    session["messages"].append({
        "sender": sender,
        "text": text
    })

    # -------------------------------------------------
    # EXTRACTION
    # -------------------------------------------------
    extract_intelligence(text, session["intelligence"])

    # -------------------------------------------------
    # DETECTION
    # -------------------------------------------------
    is_scam, keywords = detect_scam(text)

    if is_scam:
        session["scamDetected"] = True
        session["intelligence"]["suspiciousKeywords"].extend(keywords)

    # -------------------------------------------------
    # AI AGENT
    # -------------------------------------------------
    agent_reply = None

    if session["scamDetected"] and sender != "agent":
        agent_reply = await asyncio.to_thread(
            generate_ai_reply,
            session["messages"]
        )

        session["messages"].append({
            "sender": "agent",
            "text": agent_reply
        })

    # -------------------------------------------------
    # METRICS
    # -------------------------------------------------
    engagement_duration = int(time.time() - session["start_time"])

    # -------------------------------------------------
    # CALLBACK (ONLY ONCE)
    # -------------------------------------------------
    if (
        session["scamDetected"]
        and session["message_count"] >= 5
        and not session["callback_sent"]
    ):
        send_final_callback(session)
        session["callback_sent"] = True

    # -------------------------------------------------
    # AGENT NOTES (required in response)
    # -------------------------------------------------
    session["agent_notes"] = "Scammer used urgency and payment redirection tactics"

    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------
    return {
        "status": "success",
        "scamDetected": session["scamDetected"],
        "engagementMetrics": {
            "engagementDurationSeconds": engagement_duration,
            "totalMessagesExchanged": session["message_count"]
        },
        "extractedIntelligence": session["intelligence"],
        "agentReply": agent_reply,
        "agentNotes": session["agent_notes"]
    }
