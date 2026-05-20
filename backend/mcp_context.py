def get_emotion_context(user_input):
    text = user_input.lower()

    if "anxious" in text:
        return {"mode": "calm_support"}
    elif "sad" in text:
        return {"mode": "empathy_support"}
    else:
        return {"mode": "general_support"}


from backend.rag_faiss import get_context


def get_rag_context(user_input):
    return {"knowledge": get_context(user_input) or ""}


def get_user_context(user):
    if not isinstance(user, dict):
        user = {}

    return {
        "xp": user.get("todayXP", 0),
        "user_email": user.get("email", "")
    }


def get_history_context(history):
    if not history:
        return {"history": ""}

    formatted = []
    for message in history[-6:]:
        role = message.get("role", "user")
        content = message.get("content", "")
        formatted.append(f"{role}: {content}")

    return {"history": "\n".join(formatted)}


def build_mcp_context(user_input, user, history=None):
    context = {}

    context.update(get_emotion_context(user_input))
    context.update(get_rag_context(user_input))
    context.update(get_user_context(user))
    context.update(get_history_context(history))

    return context