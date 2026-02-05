import re

# -------------------------------------------------
# PRECOMPILED KEYWORDS (faster)
# -------------------------------------------------
SCAM_KEYWORDS = {
    "blocked", "suspended", "verify", "urgent", "immediate",
    "bank", "account", "upi", "transfer", "refund", "kyc",
    "click", "link", "update", "otp", "reward", "lottery",
    "prize", "cashback", "limited", "expire"
}

# quick patterns (high-confidence)
URL_REGEX = re.compile(r"https?://|www\.", re.IGNORECASE)
PHONE_REGEX = re.compile(r"(?:\+91[\s-]?)?[6-9]\d{9}\b")


# -------------------------------------------------
# SMART DETECTION (score based)
# -------------------------------------------------
def detect_scam(text: str):
    if not text:
        return False, []

    text = text.lower()

    matched = [k for k in SCAM_KEYWORDS if k in text]
    score = len(matched)

    # high-risk boosts
    if URL_REGEX.search(text):
        score += 2

    if PHONE_REGEX.search(text):
        score += 1

    # trigger rules
    is_scam = score >= 2

    return is_scam, matched
