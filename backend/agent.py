from openai import OpenAI

client = OpenAI()

def therapist_response(user_message):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a supportive therapist assistant."},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content
def safety_check(text):

    crisis_words = ["suicide", "kill myself", "self harm"]

    for word in crisis_words:
        if word in text.lower():
            return True

    return False