import os

# -------------------------------------------------
# API KEY (env overrides default)
# -------------------------------------------------
API_KEY = os.getenv("API_KEY", "sherlock_369")

# -------------------------------------------------
# CALLBACK (fixed hackathon endpoint)
# -------------------------------------------------
FINAL_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
