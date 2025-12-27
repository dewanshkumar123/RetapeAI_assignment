import re

BEEP_KEYWORDS = [
    "beep", "when you hear", "tone"
]

END_GREETING_KEYWORDS = [
    "hang up", "thanks for calling",
     "goodbye", "bye", "good day", "call you back"
]

CONVERSATION_ENDERS = [
    r"(thank|thanks)\s+(for|again)",
    r"(good\s*)?bye",
    r"take\s+care",
    r"have\s+a\s+(great|good)\s+day",
]

def mentions_beep(text):
    """Check if text explicitly mentions a beep."""
    t = text.lower()
    return any(k in t for k in BEEP_KEYWORDS)

def greeting_finished(text):
    """
    Detect greeting end using multiple strategies:
    1. Explicit end keywords
    2. Conversation enders
    """
    t = text.lower()
    
    # Strategy 1: Explicit end keywords
    # print(text)
    if any(k in t for k in END_GREETING_KEYWORDS):
        return True
    
    # Strategy 2: Conversation enders
    for pattern in CONVERSATION_ENDERS:
        if re.search(pattern, t):
            return True
    
    return False
