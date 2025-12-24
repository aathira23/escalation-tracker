# Escalation Tracker

An internal escalation intelligence platform that automatically ingests client complaints from email, uses AI agents to analyze and classify issues, and tracks resolution within a 60-day SLA.

## Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Node.js 18+ (for frontend)

### 1. Start Infrastructure

```bash
# Start PostgreSQL and Redis
docker-compose up -d
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

## First-Time Setup

1. Create the initial admin user via the API:

```bash
curl -X POST http://localhost:8000/api/auth/setup-admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "secure_password_here",
    "full_name": "System Admin"
  }'
```

2. Login to get your JWT token
3. Create clients and users through the API or frontend

## Project Structure

```
escalation-tracker/
├── docker-compose.yml     # PostgreSQL & Redis
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI entry point
│   │   ├── config.py      # Environment configuration
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── agents/        # AI agents (Gemini)
│   │   └── tasks/         # Celery background tasks
│   ├── alembic/           # Database migrations
│   └── requirements.txt
└── frontend/
    └── src/               # React TypeScript app
```

## Key Features

- **Email Ingestion**: Automatic complaint capture (mock mode for dev)
- **AI Analysis**: Gemini-powered complaint classification
- **Role-Based Access**: Admin, Manager, Viewer roles
- **SLA Tracking**: 60-day resolution window with alerts
- **Analytics**: Dashboard, client, and team metrics

## User Roles

| Role | Capabilities |
|------|-------------|
| **Admin** | Full system access |
| **Manager** | View all, assign escalations, analytics |
| **Viewer** | View all, add notes; becomes resolver when assigned |

## Background Jobs

Start Celery worker and beat scheduler:

```bash
cd backend

# Worker (processes tasks)
celery -A app.tasks.celery_app worker --loglevel=info

# Beat (schedules periodic tasks)
celery -A app.tasks.celery_app beat --loglevel=info
```

## Environment Variables

Copy `.env` from `backend/.env` and configure:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret |
| `GEMINI_API_KEY` | Google Gemini API key |
| `REDIS_URL` | Redis connection string |
| `MOCK_EMAIL_INGESTION` | Set to `true` for development |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Login, get JWT |
| `/api/auth/me` | GET | Current user info |
| `/api/users` | GET | List users |
| `/api/clients` | GET/POST | Client management |
| `/api/escalations` | GET/POST | Escalation CRUD |
| `/api/escalations/{id}/assign` | POST | Assign resolver |
| `/api/escalations/{id}/status` | PUT | Update status |
| `/api/analytics/overview` | GET | Dashboard stats |

## License

Internal use only.
