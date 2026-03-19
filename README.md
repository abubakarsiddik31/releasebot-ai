# 🤖 ReleaseBot AI

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-0.104+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.28+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

<div align="center">
  <h3>Intelligent Release Management System</h3>
  <p>Automate your release process with AI-powered release notes generation and seamless stakeholder communication</p>
</div>

---

ReleaseBot AI is a Python application that detects GitHub releases, generates release communication content, and distributes announcements.

## Stack

- Python 3.12
- FastAPI
- Streamlit
- LangGraph / LangChain
- SQLAlchemy (PostgreSQL or MySQL)
- Docker / Docker Compose

## Project Layout

```text
.
├── infra/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.postgres.yml
│   ├── docker-compose.mysql.yml
│   ├── docker-compose.prod.yml
│   ├── docker-compose.env
│   ├── init.sql
│   └── wait-for-db.sh
├── src/
│   ├── agents/
│   ├── config/
│   ├── models/
│   ├── services/
│   ├── ui/
│   └── utils/
├── .env.example
├── Makefile
├── requirements.txt
└── start.sh
```

## Prerequisites

- Docker + Docker Compose
- GitHub Personal Access Token
- OpenRouter API key
- Brevo API key

## Configuration

1. Create environment file:

```bash
cp .env.example .env
```

2. Set required values in `.env`:

- `GITHUB_TOKEN`
- `GITHUB_REPO` (format: `owner/repo`)
- `OPENROUTER_API_KEY`
- `BREVO_API_KEY`
- `BREVO_SENDER_EMAIL`
- `BREVO_SENDER_NAME`

## Running With Makefile

```bash
make help
make up
make up-mysql
make down
make logs
make logs-mysql
make build
make clean
```

## Running With Docker Compose Directly

PostgreSQL:

```bash
docker compose -f infra/docker-compose.postgres.yml up -d
```

MySQL:

```bash
docker compose -f infra/docker-compose.mysql.yml up -d
```

Stop:

```bash
docker compose -f infra/docker-compose.postgres.yml down
docker compose -f infra/docker-compose.mysql.yml down
```

## Application URLs

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Streamlit: http://localhost:8501

## Local Development (Without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

In another terminal:

```bash
source .venv/bin/activate
streamlit run src/ui/streamlit_app.py
```

## API Endpoints

- `POST /trigger-release`
- `GET /releases`
- `GET /releases/{tag}/status`
- `GET /users`
- `POST /users`
- `GET /campaigns`
- `GET /health`

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GITHUB_TOKEN` | Yes | GitHub token |
| `GITHUB_REPO` | Yes | Repository in `owner/repo` format |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key |
| `BREVO_API_KEY` | Yes | Brevo API key |
| `BREVO_SENDER_EMAIL` | Yes | Sender email |
| `BREVO_SENDER_NAME` | Yes | Sender display name |
| `DATABASE_URL` | No | Database connection string |
| `LOG_LEVEL` | No | Logging level |
| `ENVIRONMENT` | No | Runtime environment |

## Contributing

1. Create a branch from `main`
2. Keep changes focused
3. Run tests/lint locally
4. Open a pull request with a clear summary

## License

MIT. See `LICENSE`.
