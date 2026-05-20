MODE_RULES = {
    "calm_support": """
    Be gentle and calming.
    Suggest 1 quick breathing exercise.
    Keep response short (2–3 sentences).
    """,

    "empathy_support": """
    Be warm and validating.
    Focus on understanding feelings.
    Avoid giving too many solutions.
    """,

    "general_support": """
    Be helpful and friendly.
    Keep it concise.
    """
}


def get_mode_instruction(mode):
    return MODE_RULES.get(mode, MODE_RULES["general_support"])