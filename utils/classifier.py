import re

BEEP_KEYWORDS = [
    "beep", "when you hear", "tone"
]

END_GREETING_KEYWORDS = [
    "thank you", "thanks for calling",
     "goodbye"
]

# Patterns that indicate greeting is ending (instructional prompts)
INSTRUCTION_PATTERNS = [
    r"if\s+you\s+(record|leave|provide|enter|press)",  # "if you record", "if you leave"
    r"(record|leave|provide)\s+your\s+(name|message|reason)",  # "record your name"
    r"reason\s+for\s+calling",  # "reason for calling"
    r"at\s+the\s+tone",  # "at the tone"
    r"(state|say)\s+your",  # "state your name"
    r"please\s+(record|leave|provide|press|enter)",  # "please record"
]

CONVERSATION_ENDERS = [
    r"(thank|thanks)\s+(you|for|again)",
    r"(good\s*)?bye",
    r"take\s+care",
    r"have\s+a\s+(great|good)\s+day",
    r"look\s+forward",
]

def mentions_beep(text):
    """Check if text explicitly mentions a beep."""
    t = text.lower()
    return any(k in t for k in BEEP_KEYWORDS)

def greeting_finished(text):
    """
    Detect greeting end using multiple strategies:
    1. Explicit end keywords
    2. Instruction patterns (caller being given directions)
    3. Conversation enders
    """
    t = text.lower()
    
    # Strategy 1: Explicit end keywords
    if any(k in t for k in END_GREETING_KEYWORDS):
        return True
    
    # Strategy 2: Instruction patterns indicate greeting transition
    # (greeting typically followed by instructions like "please record your name")
    for pattern in INSTRUCTION_PATTERNS:
        if re.search(pattern, t):
            return True
    
    # Strategy 3: Conversation enders
    for pattern in CONVERSATION_ENDERS:
        if re.search(pattern, t):
            return True
    
    # Strategy 4: Heuristic - if text contains request for caller action
    # followed by expected silence (caller will now do the action)
    if ("your" in t and ("name" in t or "number" in t or "message" in t)):
        return True
    
    return False
