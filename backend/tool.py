def breathing_exercise():
    return "Try breathing: inhale 4 seconds, hold 4, exhale 6."

def journaling_prompt():
    return "Write about what triggered this feeling today."

from langchain.tools import Tool

tools = [
    Tool(name="Breathing", func=breathing_exercise, description="Use for stress"),
    Tool(name="Journaling", func=journaling_prompt, description="Use for reflection")
]