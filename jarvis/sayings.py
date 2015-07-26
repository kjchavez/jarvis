from random import choice

def intent_failed():
    return choice([
        "I couldn't do that.",
        "That didn't work.",
        "Sorry, I tried."])

def misunderstood():
    return choice([
        "Pardon?",
        "Could you repeat that, sir?",
        "I beg your pardon?"
        "Sorry, I didn't understand you."])
