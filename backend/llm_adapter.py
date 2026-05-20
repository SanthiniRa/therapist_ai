import time
from google.genai.errors import ServerError
from backend.agent import MODEL_NAME

class GeminiAdapter:
    def __init__(self, model):
        self.model = model
        self.model_name = MODEL_NAME

    def _call_generate(self, prompt):
        try:
            return self.model.generate_content(prompt)
        except TypeError:
            return self.model.generate_content(
                model=self.model_name,
                contents=prompt
            )

    def generate(self, prompt):
        attempts = 2
        for attempt in range(attempts):
            try:
                response = self._call_generate(prompt)
                return response.text
            except ServerError:
                if attempt == attempts - 1:
                    raise
                time.sleep(1)
