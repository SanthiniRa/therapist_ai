# TherapistAI

TherapistAI is an AI therapist support platform built with FastAPI, React, and Gemini. It combines Google OAuth login, conversation memory, mood tracking, lightweight retrieval-augmented support, and a React client for chat and wellbeing views.

## Things You Can Do

TherapistAI is built to help with reflective, therapy-style support. You can use it to:

- chat with a Gemini-powered therapist assistant
- sign in with Google through FastAPI and Authlib
- keep short-term conversation context during a session
- track mood changes over time
- use local therapy guidance files as retrieval context
- test retrieval behavior with the built-in RAG endpoint
- view chat, mood, and journal pages in the React frontend
- run the backend and frontend separately during development

## Key Features

| Capability | Description |
| --- | --- |
| Google OAuth | Signs users in with Google and stores the session in FastAPI middleware |
| AI therapist chat | Generates responses with `google-genai` and `models/gemini-2.5-flash` by default |
| Conversation memory | Stores recent user and assistant messages in memory for context |
| Mood tracking | Detects simple mood signals from user input and exposes `/mood` |
| RAG support | Pulls context from plain-text therapy guidance files in `knowledge/` |
| Rate limiting | Protects the chat endpoint with `slowapi` |
| React UI | Provides login, chat, mood chart, and journal routes |
| Debug tooling | Includes a `/test-rag` endpoint and `list_models.py` helper |

## Tech Stack Architecture

TherapistAI is a modular two-tier app: the frontend handles the user experience, while the backend owns authentication, memory, retrieval, and Gemini integration. That keeps the system simple to run locally without hiding the core AI workflow.

```text
User
  |
  v
React frontend
  |
  v
FastAPI backend
  |-- Google OAuth session handling
  |-- Chat endpoint
  |-- Mood endpoint
  |-- RAG retrieval
  |-- Memory / profile store
  |-- Rate limiting
  |
  v
Gemini API + local knowledge files
```

### Layer Breakdown

| Layer | Stack | Responsibility |
| --- | --- | --- |
| Presentation | React, React Router, Chart.js | Login, chat UI, mood chart, and journal screens |
| API layer | FastAPI, Pydantic | HTTP routes, request validation, and session-aware responses |
| Auth layer | Authlib, SessionMiddleware | Google OAuth login and session storage |
| AI layer | Google Gemini via `google-genai` | Response generation and therapist-style prompting |
| Retrieval layer | Local text files and simple RAG helpers | Supplies therapy guidance context to prompts |
| Memory layer | In-memory conversation/session/profile stores | Tracks recent messages, mood, and basic preferences |
| Safety layer | Rule-based crisis keyword check | Returns a support-first message for high-risk phrasing |
| Tooling | SlowAPI, dotenv, helper scripts | Rate limiting, env loading, and model inspection |

## System Design

The app keeps the AI flow lightweight so it is easy to understand and extend. A request enters the backend, memory and profile context are gathered, retrieval context is added from local knowledge, and Gemini generates the final reply.

### Design Choices

| Area | Choice | Trade-off |
| --- | --- | --- |
| Backend shape | Single FastAPI app with auth, chat, memory, and RAG helpers | Easy to run and reason about, but less isolated than a service split |
| Model provider | Gemini through `google-genai` | Strong model quality and a modern client, but depends on Google API credentials |
| Retrieval | Local text-file knowledge base | Fast and simple for therapy guidance, but not a production-grade vector store yet |
| State | In-memory conversation, mood, and profile stores | Great for development, but resets on restart |
| Frontend | React client with routed views | Familiar and flexible, but currently tied to hardcoded backend URLs in source files |
| Safety | Keyword-based crisis check | Lightweight and visible, but should be replaced with stronger moderation for production |

### Why This Architecture

- It keeps the product fast to iterate on while the feature set is still evolving.
- It gives the AI assistant real context without forcing a heavyweight infrastructure stack.
- It makes it easy to test retrieval, memory, and prompt behavior independently.
- It leaves room to replace in-memory state with persistent storage later.

### Data Flow

1. The user signs in through Google OAuth.
2. The frontend sends chat messages to the FastAPI backend.
3. The backend loads conversation history, session data, and the user profile.
4. The backend adds relevant knowledge from the local RAG files.
5. Gemini generates a therapist-style response using the assembled prompt.
6. The assistant reply is stored in memory and returned to the UI.
7. Mood history can be viewed separately through the mood route.

### Failure Modes

| Failure mode | Handling strategy |
| --- | --- |
| Missing API key | Raise a startup error so the backend fails fast |
| OAuth not configured | Login flow will fail until client ID and secret are set |
| Weak retrieval context | Fall back to a general supportive response |
| Gemini error | Return a gentle fallback message instead of crashing the chat request |
| Rate limit hit | Return HTTP 429 from the chat endpoint |
| Restarted backend | In-memory chat, mood, and profile data are lost |

## Getting Started

### Install Dependencies

```bash
pip install -r requirement
```

```bash
cd frontend/therapist-chat
npm install
```

### Configure Environment Variables

Create `backend/.env` with values like these:

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GENAI_MODEL=models/gemini-2.5-flash
EMBEDDING_MODEL=models/textembedding-gecko-001
```

`GENAI_API_KEY` is also supported if you prefer that name.

### Run Locally

Backend:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend/therapist-chat
npm start
```

### Helpful Scripts

```bash
python list_models.py
```

Use this to list the Gemini models available to your API key.

```bash
python test_rag.py
```

Use this to exercise the retrieval path against the backend.

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Simple backend status check |
| POST | `/chat` | Authenticated therapist chat endpoint |
| GET | `/mood` | Mood history for the signed-in user |
| POST | `/test-rag` | Debug retrieval endpoint |
| GET | `/login/google` | Starts Google OAuth login |
| GET | `/auth/google/callback` | Handles the OAuth callback |
| GET | `/user` | Returns the current session user |

## Notes

- Memory, mood logs, and profile state are currently stored in memory and reset when the backend restarts.
- The frontend source still points at a deployed GitHub Codespaces backend URL in `src/login.js`, `src/chat.js`, `src/moodChart.js`, and `src/Journal.js`. Update those URLs if you are running locally.
- The frontend includes a journal page, but the backend does not yet expose a dedicated `/journal` API route.
- `backend/auth.py` still uses a development session secret and should be moved to an environment variable before production use.

## Project Layout

```text
AILearning/
  backend/              FastAPI app, auth, memory, Gemini client, and RAG helpers
  frontend/therapist-chat/  React app
  knowledge/            Therapy guidance text used for retrieval
  list_models.py        Helper for listing available Gemini models
  test_rag.py           Small retrieval test script
```
