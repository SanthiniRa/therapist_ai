conversation_history = []

def save_message(role, content):
    conversation_history.append({"role": role, "content": content})