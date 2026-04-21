# SimpSocial Demo

Multi-dealership MVP with a shared Sarah AI assistant, dealership-scoped chat memory, lead capture, webhook notifications, and dashboard views.

## Implemented Scope
- Three seeded dealerships:
  - Sunrise Auto (`sunrise-auto`)
  - Budget Wheels (`budget-wheels`)
  - Metro Motors (`metro-motors`)
- Shared Sarah assistant with dealership-aware prompt context
- URL-based dealership chat routes:
  - `/`
  - `/d/:dealershipSlug`
- Conversation isolation by dealership
- Language selector (`english`, `spanish`) passed to prompt generation
- Dealership-scoped lead capture, scoring, and notification event logging
- Dashboard routes:
  - `/dashboard` (SimpSocial aggregate)
  - `/dashboard/:dealershipId` (dealership CRM view with vertical tabs)

## Backend
Location: `backend/`

Tech:
- FastAPI
- SQLAlchemy + SQLite
- Optional GROQ API integration (falls back to deterministic responses if key is missing)

Run:
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Key APIs:
- `GET /api/dealerships`
- `GET /api/dealerships/{slug}`
- `POST /api/conversations`
- `GET /api/conversations/{id}?dealership_id={dealershipId}`
- `POST /api/conversations/{id}/messages?dealership_id={dealershipId}`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/dealerships`
- `GET /api/dashboard/{dealershipId}`
- `GET /api/dashboard/{dealershipId}/leads`
- `GET /api/dashboard/{dealershipId}/conversations`
- `GET /api/dashboard/{dealershipId}/notifications`
- `POST /api/internal/webhooks/lead-ready` (demo receiver)

Environment (optional):
- `GROQ_API_KEY` for live model responses
- `GROQ_MODEL` (default: `llama-3.1-8b-instant`)

## Frontend
Location: `frontend/`

Tech:
- React + TypeScript
- Vite
- React Router

Run:
```bash
cd frontend
npm install
npm run dev
```

Dev URL:
- `http://localhost:5173`

## Notes
- The app starts with default dealership behavior and allows switching dealerships via selector.
- Switching dealership updates URL and creates a fresh conversation.
- Memory does not carry across dealerships.
- Notification deduplication is scoped by `(dealership_id, lead_id, event_type)`.
