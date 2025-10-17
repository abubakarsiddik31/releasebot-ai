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

## ✨ Features

- 🚀 **AI-Powered Release Notes**: Leverage advanced AI to generate comprehensive, human-readable release notes
- 🔍 **Automatic Detection**: Smart detection of new releases from your GitHub repositories
- 📊 **Analytics Dashboard**: Real-time insights into your release metrics and trends
- 📧 **Email Distribution**: Automated email campaigns with beautiful templates
- 👥 **User Management**: Target specific user groups with personalized notifications
- ⚙️ **Flexible Configuration**: Customize workflows to match your team's needs
- 🔒 **Secure Integration**: Enterprise-grade security with encrypted API connections
- 📱 **Responsive Design**: Flawless experience across all devices
- 🐳 **One-Click Deployment**: Get started in seconds with our Docker setup

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose installed
- GitHub Personal Access Token
- OpenRouter API Key (for AI features)
- Brevo API Key (for email features)

### 1️⃣ Clone & Configure

```bash
git clone https://github.com/abubakarsiddik31/releasebot-ai.git
cd releasebot-ai

# Copy environment template
cp .env.example .env

# Configure your API keys
nano .env
```

### 2️⃣ Essential Environment Variables

```env
# GitHub Integration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPO=your-username/your-repo

# AI Provider (OpenRouter)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx

# Email Service (Brevo)
BREVO_API_KEY=xkeysib-xxxxxxxxxxxxxxxxxxxxx
BREVO_SENDER_EMAIL=your-email@example.com
BREVO_SENDER_NAME=Your Name
```

### 3️⃣ Obtaining API Tokens

<details>
<summary>🔑 GitHub Personal Access Token</summary>

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "ReleaseBot AI")
4. Set an expiration date
5. Select the following scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `read:user` (Read all user profile data)
6. Click "Generate token"
7. **Important**: Copy the token immediately as you won't be able to see it again

</details>

<details>
<summary>🤖 OpenRouter API Key</summary>

1. Sign up at [OpenRouter.ai](https://openrouter.ai/)
2. Navigate to [API Keys](https://openrouter.ai/keys)
3. Click "Create new key"
4. Give your key a name (e.g., "ReleaseBot AI")
5. Set credit limits if desired
6. Copy the API key
7. Optional: Choose your preferred models in the dashboard

**Free Tier**: OpenRouter offers a free tier with generous limits for testing and small projects.

</details>

<details>
<summary>📧 Brevo API Key</summary>

1. Sign up at [Brevo](https://www.brevo.com/)
2. Navigate to [SMTP & API](https://app.brevo.com/settings/keys/api)
3. Click "Generate a new API key"
4. Give your key a descriptive name
5. Select permissions (minimum required):
   - ✅ `Campaigns` (Create and manage campaigns)
   - ✅ `Emailing` (Send transactional emails)
   - ✅ `Contacts` (Manage contacts)
6. Click "Generate"
7. Copy the API key
8. **Important**: Verify your sender email domain in [Sender Domains](https://app.brevo.com/settings/senders) before sending emails

</details>

<details>
<summary>✅ Verifying Your Setup</summary>

After configuring your `.env` file, verify everything works:

```bash
# Test GitHub token
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
     https://api.github.com/user

# Test OpenRouter API
curl -H "Authorization: Bearer YOUR_OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models

# Test Brevo API
curl -H "api-key: YOUR_BREVO_API_KEY" \
     https://api.brevo.com/v3/account
```

If all commands return successful responses, you're ready to start!

</details>

### 3️⃣ Launch with One Command

```bash
# Using Make (recommended)
make up

# Or with Docker Compose
docker-compose up -d
```

### 4️⃣ Access Your Dashboard

- 🎯 **Main Dashboard**: [http://localhost:8501](http://localhost:8501)
- 📚 **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🏗️ Architecture Overview

```mermaid
graph TB
    A[GitHub Repository] --> B[Release Detector]
    B --> C[AI Content Generator]
    C --> D[Quality Checker]
    D --> E[Email Distributor]
    E --> F[Stakeholders]
    
    G[Streamlit Dashboard] --> H[FastAPI Backend]
    H --> I[PostgreSQL/MySQL Database]
    
    J[User Management] --> H
    K[Settings] --> H
```

---

## 📦 Installation Options

### Docker Deployment (Recommended)

<table>
  <tr>
    <th>Database</th>
    <th>Command</th>
    <th>Use Case</th>
  </tr>
  <tr>
    <td>PostgreSQL</td>
    <td><code>make up-postgres</code></td>
    <td>Default, reliable choice</td>
  </tr>
  <tr>
    <td>MySQL</td>
    <td><code>make up-mysql</code></td>
    <td>High-volume deployments</td>
  </tr>
</table>

### Manual Setup

For local development without Docker:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start database
docker-compose up -d db

# Run services
uvicorn src.main:app --reload --port 8000 &
streamlit run src/ui/streamlit_app.py
```

---

## 🎯 Usage Guide

### Dashboard Navigation

| Tab | Function | Description |
|-----|----------|-------------|
| 🏠 **Home** | Overview | Monitor release status and key metrics |
| 👥 **Users** | Management | Add, edit, and manage notification recipients |
| 🚀 **Releases** | Tracking | View, process, and manage software releases |
| 📧 **Email** | Campaigns | Create and distribute release announcements |
| ⚙️ **Settings** | Configuration | Configure integrations and preferences |

### API Endpoints

<details>
<summary>📖 View API Documentation</summary>

```http
# Core Operations
POST   /api/v1/trigger-release    # Process new releases
GET    /api/v1/releases          # List all releases
POST   /api/v1/users             # Create new user
GET    /api/v1/users             # List all users
GET    /api/v1/campaigns         # List email campaigns
GET    /api/v1/health            # System health check

# Utility Endpoints
GET    /docs                     # Interactive API docs
GET    /redoc                    # ReDoc documentation
```
</details>

---

## 🛠️ Development

### Project Structure

```
src/
├── agents/          # 🤖 AI processing agents
├── config/          # ⚙️ Configuration management
├── models/          # 📊 Database models & schemas
├── services/        # 🔌 External service integrations
├── ui/              # 🎨 Streamlit frontend
│   └── pages/       # 📄 Multi-page components
└── utils/           # 🛠️ Helper utilities
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m '✨ Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🔧 Management Commands

```bash
# Container Management
make up          # Start all services
make down        # Stop all services
make restart     # Restart services
make logs        # View logs
make clean       # Clean up everything

# Development
make build       # Rebuild Docker image
make shell       # Access container shell
make test        # Run tests
make lint        # Code linting
```

---

## 🌍 Production Deployment

### Production Checklist

- [ ] Configure environment variables for production
- [ ] Set up SSL/TLS certificates
- [ ] Configure database backups
- [ ] Set up monitoring and alerts
- [ ] Review security settings
- [ ] Load test the application

### Production Command

```bash
# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔐 Security

- 🔑 All API keys are encrypted at rest
- 🛡️ CORS protection enabled
- 🚫 Rate limiting on all endpoints
- 🔒 Secure cookie handling
- 📝 Comprehensive audit logging

---

## 📊 Monitoring & Troubleshooting

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check container status
docker-compose ps

# View real-time logs
docker-compose logs -f
```

### Common Issues

<details>
<summary>🔍 Database Connection Issues</summary>

- Verify database is healthy: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- Ensure `.env` has correct credentials
- Try recreating database: `make down && make up`
</details>

<details>
<summary>🔍 GitHub API Errors</summary>

- Verify token has required permissions:
  - Repository access (read)
  - Contents access (read)
  - Metadata access (read)
- Check token hasn't expired
- Ensure repository exists and is accessible
</details>

---

## 📝 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | ✅ | - | GitHub Personal Access Token |
| `GITHUB_REPO` | ✅ | - | Repository format: `owner/repo` |
| `OPENROUTER_API_KEY` | ✅ | - | OpenRouter API Key |
| `BREVO_API_KEY` | ✅ | - | Brevo Email API Key |
| `BREVO_SENDER_EMAIL` | ✅ | - | Verified sender email |
| `DATABASE_URL` | ❌ | auto-configured | Database connection string |
| `LOG_LEVEL` | ❌ | INFO | Logging level |
| `ENVIRONMENT` | ❌ | development | Environment name |

---

## 🤝 Support

- 📧 **Email Support**: support@releasebot-ai.com
- 💬 **Discord Community**: [Join our Discord](https://discord.gg/releasebot-ai)
- 📖 **Documentation**: [docs.releasebot-ai.com](https://docs.releasebot-ai.com)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/bakar31/releasebot-ai/issues)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for powering our AI features
- [GitHub](https://github.com/) for seamless repository integration
- [Brevo](https://www.brevo.com/) for reliable email delivery
- [FastAPI](https://fastapi.tiangolo.com/) for the robust backend
- [Streamlit](https://streamlit.io/) for the beautiful frontend
