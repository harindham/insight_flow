# insightFlow

Starter monorepo for a React frontend and FastAPI backend.

## Structure
- `frontend/` React + Vite app
- `backend/` FastAPI app

## Frontend setup
```bash
cd frontend
npm install
npm run dev
```

## Backend setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:5173` for the UI and `http://localhost:8000/health` for the API health check.
