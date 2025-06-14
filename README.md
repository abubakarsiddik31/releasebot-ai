# ReleaseBot AI

An AI-powered release notification system that automatically detects GitHub releases, analyzes changes, and sends professional email notifications to users.

## Features

- Automatic GitHub release detection
- AI-powered change analysis
- Professional email content generation
- Quality assurance checks
- Email distribution via Brevo
- User management system
- Real-time monitoring dashboard

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

## Development

- FastAPI backend runs on port 8000
- Streamlit dashboard runs on port 8501
- MySQL database runs on port 3306

## Environment Variables

Required environment variables:

- GITHUB_TOKEN: GitHub personal access token
- GITHUB_REPO: Repository in format username/repo
- OPENAI_API_KEY: OpenAI API key
- BREVO_API_KEY: Brevo API key
- DATABASE_URL: MySQL connection string

## License

MIT

# **ReleaseBot AI - MVP Implementation Architecture**

## **🎯 MVP Scope & Priorities**

### **Day 1-2: Core AI Agents + GitHub Integration**

### **Day 3-4: Email Generation + Brevo Integration**

### **Day 5: Streamlit UI + Docker Packaging**

---

## **📋 Project Structure**

```
releasebot-ai/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Environment variables
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── graph.py           # LangGraph workflow
│   │   ├── release_detector.py
│   │   ├── change_analyzer.py
│   │   ├── content_generator.py
│   │   ├── quality_checker.py
│   │   └── email_distributor.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── github_service.py
│   │   ├── brevo_service.py
│   │   └── database_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py        # SQLAlchemy models
│   │   └── schemas.py         # Pydantic models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── helpers.py
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py
├── data/
│   └── users.csv              # Initial user list
└── logs/
    └── .gitkeep
```

---

## **🔧 Technical Architecture**

### **Core Technologies**

- **Backend**: FastAPI (lightweight, async)
- **AI Framework**: LangGraph (agent orchestration)
- **LLM**: OpenAI GPT-3.5-turbo (faster, cheaper for MVP)
- **Frontend**: Streamlit (rapid UI development)
- **Database**: MySQL 8.0 (Docker container)
- **Email**: Brevo API
- **Git Integration**: PyGithub
- **Containerization**: Docker + Docker Compose

### **Environment Variables**

```env
# GitHub
GITHUB_TOKEN=your_github_token
GITHUB_REPO=username/repository

# OpenAI
OPENAI_API_KEY=your_openai_key

# Brevo
BREVO_API_KEY=your_brevo_key

# Database
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=releasebot
MYSQL_USER=releasebot
MYSQL_PASSWORD=password
DATABASE_URL=mysql://releasebot:password@db:3306/releasebot

# App
DEBUG=True
LOG_LEVEL=INFO
```

---

## **🗃️ Database Schema (Minimal)**

### **MySQL Tables**

```sql
-- Track processed releases
CREATE TABLE releases_processed (
    id INT PRIMARY KEY AUTO_INCREMENT,
    release_tag VARCHAR(50) UNIQUE NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing',
    brevo_campaign_id VARCHAR(100),
    email_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User email list
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated content cache
CREATE TABLE email_content (
    id INT PRIMARY KEY AUTO_INCREMENT,
    release_tag VARCHAR(50) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (release_tag) REFERENCES releases_processed(release_tag)
);
```

---

## **🤖 LangGraph Agent Workflow**

### **Agent State Schema**

```python
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # Input
    release_tag: str
    manual_trigger: bool

    # Release Detection
    release_data: Optional[dict]
    changelog: Optional[str]

    # Change Analysis
    analyzed_changes: Optional[dict]
    feature_summary: Optional[str]

    # Content Generation
    email_subject: Optional[str]
    email_content: Optional[str]

    # Quality Check
    quality_score: Optional[float]
    quality_feedback: Optional[str]
    approved: bool

    # Email Distribution
    user_list: Optional[List[str]]
    send_status: Optional[dict]

    # Error Handling
    errors: List[str]
    retry_count: int
```

### **LangGraph Flow**

```python
# Agent workflow definition
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("detect_release", release_detector)
workflow.add_node("analyze_changes", change_analyzer)
workflow.add_node("generate_content", content_generator)
workflow.add_node("quality_check", quality_checker)
workflow.add_node("distribute_emails", email_distributor)

# Add edges with conditions
workflow.add_edge(START, "detect_release")
workflow.add_edge("detect_release", "analyze_changes")
workflow.add_edge("analyze_changes", "generate_content")
workflow.add_edge("generate_content", "quality_check")

# Conditional edge based on quality check
workflow.add_conditional_edges(
    "quality_check",
    should_send_emails,
    {
        "send": "distribute_emails",
        "regenerate": "generate_content",
        "abort": END
    }
)
workflow.add_edge("distribute_emails", END)
```

---

## **🔍 Individual Agent Specifications**

### **1. Release Detector Agent**

**Responsibility**: Monitor GitHub for new releases
**Input**: Repository URL, manual release tag
**Output**: Release data, changelog, commit diff

**Core Logic**:

- Check for new releases using GitHub API
- Compare with processed releases in DB
- Extract release notes and changelog
- Get commit diff between releases
- Validate release is worth announcing

**Error Handling**:

- API rate limiting
- Network timeouts
- Invalid release tags
- Missing changelog data

### **2. Change Analyzer Agent**

**Responsibility**: Parse and categorize changes
**Input**: Commit diff, release notes
**Output**: Structured change summary

**Core Logic**:

- Parse commit messages using regex patterns
- Categorize changes (features, fixes, improvements)
- Extract breaking changes
- Identify user-facing vs internal changes
- Generate impact assessment

**AI Prompts**:

```
Analyze these git commits and categorize them:
- New Features (user-facing functionality)
- Bug Fixes (problem resolutions)
- Improvements (enhancements to existing features)
- Breaking Changes (backward compatibility issues)

Commits: {commit_messages}
```

### **3. Content Generator Agent**

**Responsibility**: Create engaging email content
**Input**: Analyzed changes, user context
**Output**: Subject line, HTML email content

**Core Logic**:

- Transform technical changes to user benefits
- Generate compelling subject lines
- Create structured email content
- Add appropriate call-to-actions
- Ensure mobile-friendly formatting

**AI Prompts**:

```
Create an engaging product update email for these changes:
{analyzed_changes}

Requirements:
- Professional but friendly tone
- Focus on user benefits, not technical details
- Include clear sections for features/fixes/improvements
- Generate an engaging subject line
- Keep it concise but informative
```

### **4. Quality Checker Agent**

**Responsibility**: Validate generated content
**Input**: Generated email content
**Output**: Quality score, feedback, approval

**Core Logic**:

- Check for technical accuracy
- Validate against original changes
- Ensure professional tone
- Check for spam trigger words
- Verify all claims are supported

**AI Prompts**:

```
Review this product update email for quality:
{email_content}

Original changes: {analyzed_changes}

Check for:
- Technical accuracy
- Professional tone
- Clear communication
- Spam compliance
- Missing information

Provide score (1-10) and specific feedback.
```

### **5. Email Distributor Agent**

**Responsibility**: Send emails via Brevo
**Input**: Approved content, user list
**Output**: Send status, delivery metrics

**Core Logic**:

- Fetch active users from database
- Batch email sending via Brevo API
- Handle rate limiting
- Track delivery status
- Update database with results

---

## **📧 Brevo Integration Strategy**

### **Email Service Architecture**

```python
class BrevoService:
    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.client = sib_api_v3_sdk.TransactionalEmailsApi()

    async def send_bulk_emails(self, subject, content, recipients):
        # Batch processing (max 50 per request)
        # Rate limiting (300 emails/day free tier)
        # Error handling and retry logic
        # Status tracking

    async def get_campaign_stats(self, campaign_id):
        # Fetch delivery metrics
        # Parse engagement data
        # Return structured results
```

### **Email Template Structure**

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{subject}}</title>
  </head>
  <body>
    <div class="container">
      <h1>🚀 {{app_name}} {{version}} is Live!</h1>

      {{#if new_features}}
      <section class="features">
        <h2>✨ New Features</h2>
        {{#each new_features}}
        <div class="feature">
          <h3>{{title}}</h3>
          <p>{{description}}</p>
        </div>
        {{/each}}
      </section>
      {{/if}} {{#if bug_fixes}}
      <section class="fixes">
        <h2>🐛 Bug Fixes</h2>
        <ul>
          {{#each bug_fixes}}
          <li>{{description}}</li>
          {{/each}}
        </ul>
      </section>
      {{/if}}

      <footer>
        <p>Happy coding!<br />The {{app_name}} Team</p>
      </footer>
    </div>
  </body>
</html>
```

---

## **🖥️ Streamlit UI Components**

### **Main Dashboard**

```python
# pages/01_Dashboard.py
def main_dashboard():
    st.title("🤖 ReleaseBot AI Dashboard")

    # Repository Status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Repository", "Connected ✅")
    with col2:
        st.metric("Last Release", "v1.2.3")
    with col3:
        st.metric("Emails Sent", "156")

    # Quick Actions
    st.subheader("Quick Actions")

    # Manual trigger
    release_tag = st.text_input("Release Tag (optional)")
    if st.button("🚀 Process Latest Release"):
        trigger_release_processing(release_tag)

    # Recent Activity
    st.subheader("Recent Activity")
    display_recent_campaigns()
```

### **Email Preview Page**

```python
# pages/02_Email_Preview.py
def email_preview():
    st.title("📧 Email Preview")

    # Select release
    releases = get_processed_releases()
    selected_release = st.selectbox("Select Release", releases)

    if selected_release:
        email_data = get_email_content(selected_release)

        # Preview email
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Email Preview")
            st.components.v1.html(email_data['content'], height=600)

        with col2:
            st.subheader("Email Details")
            st.write(f"**Subject:** {email_data['subject']}")
            st.write(f"**Recipients:** {email_data['recipient_count']}")
            st.write(f"**Status:** {email_data['status']}")

            # Actions
            if st.button("📤 Send Now"):
                send_emails(selected_release)
```

### **User Management Page**

```python
# pages/03_Users.py
def user_management():
    st.title("👥 User Management")

    # Add single user
    with st.expander("Add Single User"):
        email = st.text_input("Email Address")
        name = st.text_input("Name (optional)")
        if st.button("Add User"):
            add_user(email, name)

    # Bulk import
    with st.expander("Bulk Import"):
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)
            if st.button("Import Users"):
                bulk_import_users(df)

    # User list
    st.subheader("Current Users")
    users = get_all_users()
    st.dataframe(users)
```

---

## **🐳 Docker Configuration**

### **docker-compose.yml**

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000" # FastAPI
      - "8501:8501" # Streamlit
    depends_on:
      - db
    environment:
      - DATABASE_URL=mysql://releasebot:password@db:3306/releasebot
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=releasebot
      - MYSQL_USER=releasebot
      - MYSQL_PASSWORD=password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

volumes:
  mysql_data:
```

### **Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 8000 8501

# Start script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
```

---

## **⚡ 5-Day Development Sprint**

### **Day 1: Foundation & GitHub Integration**

- [ ] Set up project structure
- [ ] Configure Docker environment
- [ ] Implement GitHub service
- [ ] Create database models
- [ ] Basic LangGraph setup
- [ ] Release detector agent

### **Day 2: AI Agents Core Logic**

- [ ] Change analyzer agent
- [ ] Content generator agent
- [ ] Quality checker agent
- [ ] LangGraph workflow integration
- [ ] Error handling & logging
- [ ] Unit tests for agents

### **Day 3: Email System**

- [ ] Brevo service integration
- [ ] Email distributor agent
- [ ] HTML email templates
- [ ] Database operations
- [ ] End-to-end workflow testing

### **Day 4: Streamlit UI**

- [ ] Dashboard page
- [ ] Email preview page
- [ ] User management page
- [ ] Manual trigger functionality
- [ ] Real-time status updates

### **Day 5: Polish & Deployment**

- [ ] Docker optimization
- [ ] Error handling improvement
- [ ] Documentation
- [ ] Demo data setup
- [ ] Final testing
- [ ] Deployment scripts

---

## **🎯 Demo Success Criteria**

### **Core Functionality**

- [ ] Connect to GitHub repository
- [ ] Detect new releases automatically
- [ ] Generate professional email content
- [ ] Send emails via Brevo
- [ ] Track email delivery status

### **UI Requirements**

- [ ] Clean, intuitive dashboard
- [ ] Email preview functionality
- [ ] User management interface
- [ ] Real-time processing status
- [ ] Error handling with user feedback

### **Technical Requirements**

- [ ] Docker one-command deployment
- [ ] Robust error handling
- [ ] Proper logging
- [ ] Database persistence
- [ ] API rate limiting compliance

### **Demo Script**

1. **Setup**: `docker-compose up -d`
2. **Configuration**: Add GitHub token, Brevo API key
3. **User Import**: Upload user CSV
4. **Trigger**: Process latest release
5. **Preview**: Show generated email
6. **Send**: Distribute to users
7. **Analytics**: View delivery status

This architecture prioritizes **robust AI agent functionality** while keeping the overall system simple enough to build in 5 days, yet impressive enough for senior-level portfolio demonstration.
