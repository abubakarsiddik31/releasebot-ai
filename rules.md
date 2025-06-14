# ReleaseBot AI - Development Rules and Guidelines

## 🏗️ Application Architecture Rules

### **Project Structure Standards**

- **Strict Adherence**: Follow the exact directory structure specified in the architecture document
- **Import Conventions**: Use relative imports within packages, absolute imports between packages
- **File Naming**: Use snake_case for Python files, PascalCase for classes, UPPER_CASE for constants
- **Module Organization**: Each module should have a single, clear responsibility
- **Configuration Centralization**: All configuration must go through `src/config/settings.py`

### **Python Code Standards**

- **Python Version**: Use Python 3.11+ features where beneficial
- **Type Hints**: All function signatures must include type hints
- **Docstrings**: Use Google-style docstrings for all classes and functions
- **Error Handling**: Use structured exceptions with proper error messages
- **Async/Await**: Use async/await for all I/O operations (database, API calls)
- **Code Formatting**: Use Black for code formatting, isort for import sorting

### **Database Rules**

- **ORM Only**: All database operations must use SQLAlchemy ORM
- **Session Management**: Use dependency injection for database sessions
- **Migration Strategy**: Use Alembic for database migrations (implement in later phases)
- **Connection Pooling**: Configure proper connection pooling for production
- **Transaction Management**: Use proper transaction boundaries for data consistency
- **No Raw SQL**: Avoid raw SQL queries unless absolutely necessary for performance

### **API Design Standards**

- **RESTful Design**: Follow REST conventions for endpoint design
- **HTTP Status Codes**: Use appropriate HTTP status codes for all responses
- **Request/Response Models**: All endpoints must use Pydantic models for validation
- **Error Responses**: Standardized error response format across all endpoints
- **API Versioning**: Prepare for API versioning (v1 prefix for all endpoints)
- **Rate Limiting**: Implement rate limiting on all public endpoints

### **AI Agent Implementation Rules**

- **State Management**: All agent state must be immutable and tracked
- **Error Propagation**: Agents must handle and propagate errors through the workflow
- **Logging**: Every agent action must be logged with context
- **Retry Logic**: Implement exponential backoff for external API calls
- **Prompt Engineering**: Store all AI prompts in configuration files, not hardcoded
- **Token Management**: Monitor and limit token usage for cost control

### **Security Requirements**

- **Environment Variables**: Never hardcode secrets, always use environment variables
- **API Key Management**: Implement proper API key rotation and validation
- **Input Validation**: Validate all user inputs using Pydantic models
- **SQL Injection Prevention**: Use parameterized queries only
- **Authentication**: Implement proper authentication for production deployment
- **CORS Configuration**: Configure CORS properly for production

### **Performance Standards**

- **Async Operations**: Use async/await for all I/O operations
- **Database Queries**: Optimize database queries with proper indexing
- **Caching Strategy**: Implement caching for frequently accessed data
- **Resource Limits**: Set proper resource limits for Docker containers
- **Connection Pooling**: Use connection pooling for database and HTTP clients
- **Memory Management**: Implement proper memory management for large datasets

## 🔧 Development Workflow Rules

### **Git Workflow Standards**

- **Branch Naming**: Use task-based branch naming (e.g., `feature/T001-project-structure`)
- **Commit Messages**: Use conventional commit format with task references
- **Pull Requests**: Each task should result in a single, focused pull request
- **Code Reviews**: All code must be reviewed before merging
- **Testing**: All code must pass tests before merging
- **Documentation**: Update documentation with code changes

### **Testing Requirements**

- **Unit Tests**: Every function and class must have unit tests
- **Integration Tests**: Test all API endpoints and database operations
- **Mocking**: Use proper mocking for external services (GitHub, Brevo)
- **Test Coverage**: Maintain >80% test coverage
- **Test Data**: Use fixtures for consistent test data
- **Performance Tests**: Include performance tests for critical paths

### **Environment Management**

- **Development Environment**: Use Docker for consistent development environment
- **Environment Variables**: Use `.env` files for local development
- **Configuration Management**: Separate configuration for dev/staging/production
- **Database Migrations**: Test all migrations on development data
- **Dependency Management**: Pin all dependency versions for reproducibility

### **Error Handling Standards**

- **Exception Hierarchy**: Create custom exception classes for different error
