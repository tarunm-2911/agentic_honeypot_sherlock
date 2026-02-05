import re

def extract_intelligence(text: str, intelligence: dict):

    # UPI IDs
    upi_pattern = r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b"
    intelligence["upiIds"].extend(re.findall(upi_pattern, text))

    # Bank account numbers
    bank_pattern = r"\b\d{9,18}\b"
    intelligence["bankAccounts"].extend(re.findall(bank_pattern, text))

    # URLs
    url_pattern = r"https?://[^\s]+"
    intelligence["phishingLinks"].extend(re.findall(url_pattern, text))

    # Indian phone numbers
    phone_pattern = r"(?:\+91[\s-]?)?\b[6-9]\d{9}\b"
    intelligence["phoneNumbers"].extend(re.findall(phone_pattern, text))
