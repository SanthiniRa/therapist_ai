def build_prompt(context, user_input):
    mode_instruction = context.get("mode_instruction", context["mode"])
    history_text = context.get("history", "")
    profile_text = "" if not context.get("profile") else f"User profile: {context['profile']}\n\n"
    retrieved_knowledge = context.get('knowledge', '').strip()
    knowledge_block = retrieved_knowledge or "No relevant external knowledge was found for this query."

    return f"""
Mode: {context['mode']}

Instructions:
{context['mode']} behavior:
{mode_instruction}

User XP: {context['xp']}

Retrieved Knowledge (with sources):
{knowledge_block}

{profile_text}Conversation History:
{history_text}

Rules:
- Use retrieved knowledge if it is helpful.
- Mention source labels when helpful.
- Keep response short and empathetic.
- Avoid suggesting medical diagnoses.

User: {user_input}
"""
