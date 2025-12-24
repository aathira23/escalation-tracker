# How to Run Escalation Tracker

This guide explains how to start the full stack: Database, Backend, and Frontend.

## 1. Start Support Services (Postgres & Redis)
The database and cache are containerized.

```bash
# In the root directory
sudo docker compose up -d
```
*Note: If you run into permission errors, ensure you use `sudo` or add your user to the docker group.*

## 2. Start the Backend (FastAPI)
The backend runs on port `8000`.

```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

## 3. Start the Frontend (React)
The frontend runs on port `5173`.

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the dev server
npm run dev
```
- Application: [http://localhost:5173/](http://localhost:5173/)

## 4. Run Email Ingestion (Optional)
To process emails (or mock emails) in the background:

```bash
# Open a new terminal in /backend (with venv activated)
celery -A app.tasks.celery_app worker --loglevel=info
```
