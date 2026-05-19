def load_knowledge():
    try:
        with open("data/therapy_knowledge.txt", "r") as f:
            return f.readlines()
    except:
        return []


def get_context(user_input: str):
    knowledge_lines = load_knowledge()

    # simple keyword matching
    relevant = [
        line for line in knowledge_lines
        if any(word in line.lower() for word in user_input.lower().split())
    ]

    # fallback if nothing matches
    if not relevant:
        return "".join(knowledge_lines[:5])

    return "".join(relevant[:5])