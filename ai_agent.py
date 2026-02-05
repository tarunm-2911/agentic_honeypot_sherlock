import ollama

SYSTEM_PROMPT = (
    "You are a cautious bank customer. "
    "Reply in 1 short sentence only. "
    "Maximum 12 words. "
    "Ask one simple clarification question. "
    "Sound worried. "
    "Never share sensitive info."
)


def generate_ai_reply(messages):

    chat = [{"role": "system", "content": SYSTEM_PROMPT}]

    # ✅ use last 6 messages for better realism
    for msg in messages[-6:]:
        role = "user" if msg["sender"] == "scammer" else "assistant"
        chat.append({"role": role, "content": msg["text"][:200]})

    response = ollama.chat(
        model="phi3:mini",
        messages=chat,
        options={
            "num_predict": 18,
            "temperature": 0.2,
            "top_p": 0.8,
            "num_ctx": 512
        }
    )

    reply = response["message"]["content"].strip()
    reply = reply.split(".")[0].strip()[:120]

    return reply
