# AILearning

This repository contains a simple therapist chat application with a FastAPI backend and a React frontend.

## Development

1. **Backend**
   - Install Python requirements (`pip install -r requirement`).
   - Set your generative API key in an environment variable before starting the
     server. By default the code looks for `GENAI_API_KEY`; `GOOGLE_API_KEY` is
     also supported. For Vertex AI usage, also set `GOOGLE_CLOUD_PROJECT` and
     `GOOGLE_CLOUD_LOCATION` (e.g., `us-central1`).

     > **⚠️ Breaking change:** the code now imports `google.genai` instead of
     > the retired `google.generativeai` package. Ensure you have installed
     > `google-genai` (`pip install google-genai`) when setting up your
     > environment. The API has changed: instead of global configuration, it
     > now uses a client instance. The code now uses Vertex AI mode by default
     > to access more models. If you get a 404 error about the model not
     > being found, run `python list_models.py` to see available models and
     > update the model name in `backend/agent.py` accordingly.
     ```bash
     export GENAI_API_KEY="AIzaSyCbsqht0mYD9-VsWYGJw7w_lHweVzFmvgg"
     # or export GOOGLE_API_KEY=...
     ```
   - Optional environment variables for backend configuration:
     - `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — Google OAuth credentials
     - `SESSION_SECRET` — secret used for session cookies
     - `CORS_ALLOW_ORIGINS` — comma-separated frontend origins
     - `OAUTH_CALLBACK_URL` — backend callback URL for Google OAuth
     - `OAUTH_POST_LOGIN_REDIRECT` — frontend redirect after login
     - `MODEL_NAME` — Gemini model identifier
     - `RAG_DATA_DIR` — directory for knowledge corpus files
   - Run the server from the `backend` directory:
     ```bash
     cd backend
     uvicorn main:app --reload --host 0.0.0.0 --port 8000
     ```
   - The API will be available at `http://localhost:8000` (or the forwarded
    address when using Codespaces).  Note that the backend now enforces the
    presence of the API key at startup; if `GENAI_API_KEY`/`GOOGLE_API_KEY`
    isn't set the server will refuse to start and will print an explanatory
    error.  This early failure helps catch configuration issues sooner.
2. **Frontend**
   - Change to `frontend/therapist-chat` and run `npm install` if needed.
   - Start the React app with `npm start`.
   - The app will proxy API requests to the backend (`/chat`) using the
     `proxy` setting in `package.json`.

> ⚠️ Make sure the backend is running before sending messages; otherwise the
> UI will show a "Failed to fetch" error.

## Testing and Evaluation

- Run backend tests with:
  ```bash
  cd /workspaces/therapist_ai
  PYTHONPATH=. pytest -q tests
  ```
- New coverage includes:
  - configuration loading and env parsing
  - RAG data loading, chunking, and source-aware retrieval
  - controller fallback when the LLM service fails
- For evaluation, check:
  - whether retrieved knowledge mentions source labels
  - whether the model response remains empathetic when knowledge is missing
  - whether rate limiting and auth behavior work correctly in the UI

