# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import time
import secrets

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader

from config import API_KEY
from session_store import get_session
from detector import detect_scam
from extractor import extract_intelligence
from agent import generate_agent_reply  # ✅ rule-based agent only
from callback import send_final_callback


# -------------------------------------------------
# APP SETUP (API ONLY)
# -------------------------------------------------
app = FastAPI(
    title="Agentic Honeypot",
    description="Agentic Honeypot System – Scam detection & engagement API",
    version="1.0.0"
)


# -------------------------------------------------
# API KEY SECURITY (Swagger compatible)
# -------------------------------------------------
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def validate_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key missing")

    if not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key


# -------------------------------------------------
# MAIN ENDPOINT (CLOUD SAFE – NO OLLAMA)
# -------------------------------------------------
@app.post("/api/honeypot/message")
async def honeypot(
    payload: dict,
    _: str = Security(validate_api_key)
):
    """
    Accepts scam messages, detects scam intent,
    engages rule-based agent, extracts intelligence,
    returns structured JSON response.
    """

    # -----------------------------
    # SESSION
    # -----------------------------
    session = get_session(payload["sessionId"])

    sender = payload["message"]["sender"]
    text = payload["message"]["text"]

    session["message_count"] += 1
    session["messages"].append({
        "sender": sender,
        "text": text
    })

    # -----------------------------
    # ALWAYS EXTRACT INTELLIGENCE
    # -----------------------------
    extract_intelligence(text, session["intelligence"])

    # -----------------------------
    # SCAM DETECTION
    # -----------------------------
    is_scam, keywords = detect_scam(text)

    if is_scam:
        session["scamDetected"] = True
        session["intelligence"]["suspiciousKeywords"].extend(keywords)

    # -----------------------------
    # RULE-BASED AGENT (instant + safe)
    # -----------------------------
    agent_reply = None

    if session["scamDetected"] and sender != "agent":
        agent_reply = generate_agent_reply(session["message_count"])

        session["messages"].append({
            "sender": "agent",
            "text": agent_reply
        })

    # -----------------------------
    # METRICS
    # -----------------------------
    engagement_duration = int(time.time() - session["start_time"])

    # -----------------------------
    # FINAL CALLBACK
    # -----------------------------
    if session["scamDetected"] and session["message_count"] >= 5:
        send_final_callback(session)

    # -----------------------------
    # RESPONSE (ALWAYS JSON)
    # -----------------------------
    return {
        "status": "success",
        "scamDetected": session["scamDetected"],
        "engagementMetrics": {
            "engagementDurationSeconds": engagement_duration,
            "totalMessagesExchanged": session["message_count"]
        },
        "extractedIntelligence": session["intelligence"],
        "agentReply": agent_reply
    }
