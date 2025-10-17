# ReleaseBot AI

ReleaseBot AI is an intelligent release management system that automates the process of detecting, analyzing, and communicating software releases. It uses AI to generate high-quality release notes and ensures timely delivery to stakeholders.

## Features

- 🤖 AI-powered release note generation
- 🔍 Automatic release detection from GitHub
- 📊 Comprehensive analytics dashboard
- 📧 Automated email distribution
- 👥 User management and targeting
- ⚙️ Configurable workflow settings
- 🔒 Secure API integrations
- 📱 Responsive web interface
- 🐳 Full Docker support with single command setup

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker with our unified setup:

1. Clone the repository:

```bash
git clone https://github.com/bakar31/releasebot-ai.git
cd releasebot-ai
```

2. Configure your environment variables:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys and preferences
nano .env  # or use your preferred editor
```

Required environment variables:
```env
# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo

# Brevo Configuration (for email)
BREVO_API_KEY=your_brevo_api_key_here
BREVO_SENDER_EMAIL=your_verified_email@example.com
BREVO_SENDER_NAME=Your Name

# OpenRouter Configuration (for AI)
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

3. Start the application with one command (using PostgreSQL by default):

```bash
# Option 1: Using Make (easiest)
make up

# Option 2: Using Docker Compose directly
docker-compose up -d
```

4. Access the application:
- Dashboard: http://localhost:8501
- API Documentation: http://localhost:8000/docs

### Database Options

The application supports both PostgreSQL and MySQL databases:

```bash
# Use PostgreSQL (default)
make up-postgres
# or
make up

# Use MySQL
make up-mysql
```

## Docker Commands

Use the following commands to manage the application:

```bash
# Start the application (PostgreSQL by default)
make up

# Start with specific database
make up-postgres  # PostgreSQL
make up-mysql     # MySQL

# Stop the application
make down

# View logs
make logs

# Clean up everything (remove all containers, volumes, and images)
make clean

# Rebuild the image
make build
```

## Manual Docker Setup

If you prefer not to use the Makefile:

1. Set database configuration:
```bash
# For PostgreSQL
source docker-compose.env postgres

# For MySQL
source docker-compose.env mysql
```

2. Start the services:
```bash
docker-compose up -d
```

## Development Setup

For local development without Docker:

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the database:

```bash
docker-compose up -d db
```

4. Run the application:

```bash
# Run the FastAPI backend
uvicorn src.main:app --reload --port 8000

# Run the Streamlit frontend (in another terminal)
streamlit run src/ui/streamlit_app.py
```

## Project Structure

```
releasebot-ai/
├── src/
│   ├── agents/           # AI agents for release processing
│   ├── config/          # Configuration settings
│   ├── models/          # Database models and schemas
│   ├── services/        # External service integrations
│   ├── ui/              # Streamlit frontend
│   └── utils/           # Utility functions
├── .env.example         # Environment variables template
├── docker-compose.yml   # Unified Docker configuration
├── docker-compose.prod.yml  # Production Docker configuration
├── docker-compose.env   # Database configuration helper
├── Dockerfile          # Docker build instructions
├── Makefile            # Convenient commands
└── requirements.txt    # Python dependencies
```

## Usage

### Dashboard

1. Access the dashboard at http://localhost:8501
2. Configure your GitHub repository and API keys in the Settings tab
3. Monitor release status and metrics in the main dashboard
4. Use the manual trigger button to process releases on demand

### Email Management

1. Navigate to the Email Preview tab
2. Select a release campaign to preview
3. Review and edit email content if needed
4. Send test emails or distribute to all users

### User Management

1. Go to the User Management tab
2. Add users individually or import via CSV
3. Manage user status and preferences
4. View user analytics and engagement metrics

## API Documentation

The API documentation is available at http://localhost:8000/docs when running the application. Key endpoints include:

- `POST /trigger-release`: Process new releases
- `GET /releases`: List all releases
- `GET /users`: List all users
- `POST /users`: Create a new user
- `GET /campaigns`: List email campaigns
- `GET /health`: Health check endpoint

## Production Deployment

For production deployment:

1. Use the production Docker Compose configuration:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. Configure SSL certificates for secure access
3. Set up proper backup procedures for the database
4. Configure monitoring and alerting

## Environment Variables

The application uses the following environment variables:

### Required
- `GITHUB_TOKEN`: GitHub personal access token
- `BREVO_API_KEY`: Brevo email service API key
- `BREVO_SENDER_EMAIL`: Verified sender email
- `OPENROUTER_API_KEY`: OpenRouter API key for AI services

### Optional
- `DATABASE_URL`: Database connection URL (auto-configured)
- `API_BASE_URL`: Base URL for the API (default: http://localhost:8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `ENVIRONMENT`: Environment name (default: development)

## Troubleshooting

### Database Connection Issues
- Ensure the database container is healthy: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- Verify environment variables in `.env`

### Application Won't Start
- Check all required environment variables are set
- Verify Docker and Docker Compose are installed
- Check port conflicts (8000 for API, 8501 for UI)

### Performance Issues
- For high-volume use, consider using MySQL instead of PostgreSQL
- Monitor resource usage with `docker stats`
- Adjust memory limits in docker-compose.prod.yml

## Acknowledgments

- OpenAI for AI capabilities
- GitHub for repository integration
- Brevo for email services
- FastAPI for the backend framework
- Streamlit for the frontend interface
