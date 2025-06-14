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

## Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose
- MySQL 8.0
- GitHub account with repository access
- Brevo account for email services
- OpenRouter API key for AI services

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/yourusername/releasebot-ai.git
cd releasebot-ai
```

2. Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

3. Update the `.env` file with your credentials:

```env
# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_REPO_OWNER=your_username
GITHUB_REPO_NAME=your_repo

# Brevo Configuration
BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_EMAIL=your_verified_email
BREVO_SENDER_NAME=Your Name

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key

# Database Configuration
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=releasebot
MYSQL_USER=releasebot
MYSQL_PASSWORD=your_password
```

4. Start the application using Docker Compose:

```bash
docker-compose up -d
```

5. Access the application:

- Dashboard: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## Development Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
# Start the database
docker-compose up -d db

# Run the FastAPI backend
uvicorn src.api.main:app --reload --port 8000

# Run the Streamlit frontend
streamlit run src/ui/streamlit_app.py
```

## Project Structure

```
releasebot-ai/
├── src/
│   ├── agents/           # AI agents for release processing
│   ├── api/             # FastAPI backend
│   ├── config/          # Configuration settings
│   ├── db/              # Database models and migrations
│   ├── services/        # External service integrations
│   ├── ui/              # Streamlit frontend
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── .env.example         # Environment variables template
├── docker-compose.yml   # Development Docker configuration
├── docker-compose.prod.yml  # Production Docker configuration
├── Dockerfile          # Docker build instructions
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

- `POST /api/v1/releases/process`: Process new releases
- `GET /api/v1/releases`: List all releases
- `POST /api/v1/emails/send`: Send release emails
- `GET /api/v1/users`: List all users

## Production Deployment

For production deployment:

1. Use the production Docker Compose configuration:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. Configure SSL certificates for secure access
3. Set up proper backup procedures for the database
4. Configure monitoring and alerting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:

1. Check the documentation
2. Open an issue on GitHub
3. Contact the maintainers

## Acknowledgments

- OpenAI for AI capabilities
- GitHub for repository integration
- Brevo for email services
- FastAPI for the backend framework
- Streamlit for the frontend interface
