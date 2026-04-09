# Architecture Documentation - Instagram Upload Service

**Created by:** Alex Technical Architect (Arquitecto)  
**Date:** 2026-04-08  
**Version:** 1.0

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Principles](#architecture-principles)
- [Component Design](#component-design)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Error Handling](#error-handling)
- [Scalability Considerations](#scalability-considerations)

## System Overview

### Purpose
The Instagram Upload Service automates the process of uploading videos to Instagram Reels using browser automation via Playwright. It provides a complete solution including authentication, session management, video upload, and error handling.

### Key Features
1. **Instagram Authentication:** Login with username/password and 2FA support
2. **Session Persistence:** Cookie management with encryption
3. **Video Upload:** Automated upload through Instagram web interface
4. **Error Recovery:** Automatic retry and error handling
5. **Async Processing:** Support for background upload tasks

### Technology Stack
- **Automation:** Playwright Python
- **Async Tasks:** Celery + Redis
- **Database:** PostgreSQL (for job tracking)
- **Testing:** Pytest with full coverage
- **Monitoring:** Prometheus metrics

## Architecture Principles

### SOLID Principles Applied
1. **Single Responsibility:** Each class has one clear purpose
2. **Open/Closed:** Open for extension, closed for modification
3. **Liskov Substitution:** Subtypes replaceable by base types
4. **Interface Segregation:** Specific interfaces over general ones
5. **Dependency Inversion:** Depend on abstractions, not concretions

### Design Patterns
1. **Service Pattern:** `BrowserService`, `LoginManager`, `CookieManager`
2. **Factory Pattern:** Browser configuration and creation
3. **Strategy Pattern:** Different authentication strategies
4. **Observer Pattern:** Event handling for upload status
5. **Retry Pattern:** Exponential backoff for failures

### Quality Attributes
- **Maintainability:** Clear separation of concerns, SOLID principles
- **Testability:** Dependency injection, mockable interfaces
- **Security:** Encryption, secure credential handling
- **Reliability:** Error recovery, session persistence
- **Performance:** Async operations, efficient resource usage

## Component Design

### Authentication Module (`src/auth/`)

#### BrowserService
**Purpose:** High-level browser automation management

**Key Responsibilities:**
- Browser lifecycle management
- Context and page management
- Human-like interaction simulation
- Screenshot capture for debugging

**Class Structure:**
```python
class BrowserService:
    def __init__(config: BrowserConfig)
    async def initialize() -> None
    async def navigate_to_instagram() -> None
    async def human_like_delay() -> None
    async def type_like_human() -> None
    async def save_cookies() -> None
    async def load_cookies() -> None
```

#### LoginManager
**Purpose:** Instagram authentication with 2FA support

**Key Responsibilities:**
- Credential validation and management
- Login flow automation
- Two-factor authentication handling
- Error detection and reporting

**Class Structure:**
```python
class InstagramLoginManager:
    def __init__()  # Loads from .env.instagram
    async def login() -> bool
    async def login_with_cookies() -> bool
    async def _perform_initial_login() -> bool
    async def _handle_two_factor_auth() -> bool
```

#### CookieManager
**Purpose:** Secure session cookie management

**Key Responsibilities:**
- Cookie encryption/decryption
- Session expiration tracking
- Backup and recovery
- Secure storage

**Class Structure:**
```python
class CookieManager:
    def __init__()  # Configures from environment
    def save_cookies(cookies: List[Dict], username: str) -> bool
    def load_cookies() -> Tuple[List[Dict], SessionInfo]
    def has_valid_session() -> bool
    def invalidate_session() -> bool
```

### Core Module (`src/core/`)

#### RetryManager
**Purpose:** Exponential backoff and retry logic

**Key Responsibilities:**
- Configurable retry strategies
- Exponential backoff calculation
- Failure classification
- Circuit breaker pattern

#### ErrorHandler
**Purpose:** Centralized error handling

**Key Responsibilities:**
- Error classification and routing
- CAPTCHA detection and handling
- Rate limiting detection
- Recovery strategies

### Upload Module (`src/upload/`) - Future Development

#### VideoUploader
**Purpose:** Video upload automation

**Key Responsibilities:**
- File selection and validation
- Upload progress monitoring
- Instagram UI interaction

#### MetadataHandler
**Purpose:** Video metadata management

**Key Responsibilities:**
- Caption and hashtag processing
- Location and tagging
- Visibility settings

## Data Flow

### Authentication Flow
```
1. User Configuration
   ↓
2. Browser Initialization
   ↓
3. Instagram Navigation
   ↓
4. Cookie Check (if exists)
   ↓
5. Login Attempt
   ↓
6. 2FA Handling (if required)
   ↓
7. Session Persistence
   ↓
8. Ready for Upload
```

### Cookie Management Flow
```
1. Login Success
   ↓
2. Extract Cookies
   ↓
3. Encrypt (if key provided)
   ↓
4. Store with Metadata
   ↓
5. Set Expiration
   ↓
6. Next Request: Load & Validate
```

### Error Recovery Flow
```
1. Operation Attempt
   ↓
2. Error Detection
   ↓
3. Classification
   ↓
4. Retry Decision
   ↓
5. Recovery Action
   ↓
6. Success or Escalation
```

## Security Architecture

### Credential Security
- **Storage:** Environment variables only
- **Transmission:** HTTPS only for Instagram
- **Memory:** Cleared after use
- **Backup:** Encrypted if stored

### Session Security
- **Cookie Encryption:** AES-256 if key provided
- **HttpOnly Flag:** Prevents JavaScript access
- **Secure Flag:** HTTPS only
- **SameSite:** Strict mode
- **Expiration:** Configurable timeout

### Data Protection
- **At Rest:** Encryption for sensitive data
- **In Transit:** HTTPS/TLS
- **Access Control:** File permissions
- **Audit Trail:** Logging of sensitive operations

### Threat Mitigation
1. **Account Lockout:** Rate limiting simulation
2. **CAPTCHA Handling:** Detection and manual intervention
3. **Behavior Analysis:** Human-like interaction patterns
4. **Monitoring:** Suspicious activity detection

## Error Handling

### Error Classification

#### Authentication Errors
- `ConfigurationError`: Missing or invalid configuration
- `AuthenticationError`: Login failed
- `TwoFactorRequiredError`: 2FA needed but not provided
- `TwoFactorInputError`: Invalid 2FA code

#### Browser Errors
- `BrowserError`: General browser issues
- `BrowserInitError`: Browser startup failed
- `BrowserNotInitializedError`: Using browser before init

#### Network Errors
- Timeout errors
- Connection failures
- Rate limiting responses

### Recovery Strategies

#### Automatic Recovery
1. **Retry with Backoff:** Exponential delay between retries
2. **Session Refresh:** Clear cookies and retry login
3. **Browser Restart:** Fresh browser instance

#### Manual Intervention
1. **2FA Input:** Pause for user input
2. **CAPTCHA Solving:** Manual completion
3. **Account Unlock:** User action required

#### Escalation Path
```
1. Automatic Retry (3 attempts)
   ↓
2. Session Refresh (1 attempt)
   ↓
3. Browser Restart (1 attempt)
   ↓
4. Manual Intervention Required
```

### Logging and Monitoring
- **Error Logs:** Detailed error information
- **Screenshots:** Visual debugging aids
- **Metrics:** Success/failure rates
- **Alerts:** Critical failure notifications

## Scalability Considerations

### Horizontal Scaling
- **Stateless Design:** Session stored externally
- **Browser Pooling:** Reuse browser instances
- **Load Distribution:** Multiple Instagram accounts

### Performance Optimization
- **Connection Pooling:** Reuse HTTP connections
- **Cookie Caching:** Reduce storage I/O
- **Async Operations:** Non-blocking I/O

### Resource Management
- **Browser Memory:** Cleanup after operations
- **Connection Limits:** Rate limiting compliance
- **Disk Usage:** Log rotation and cleanup

### Monitoring and Metrics
- **Performance Metrics:** Operation timing
- **Resource Usage:** CPU, memory, disk
- **Success Rates:** Upload completion statistics
- **Error Rates:** Failure classification

## Deployment Architecture

### Development Environment
- Local browser automation
- Debug mode enabled
- Detailed logging
- Manual intervention support

### Staging Environment
- Headless browser operation
- Real Instagram test account
- Performance testing
- Integration testing

### Production Environment
- Multiple worker instances
- Load balancing
- High availability
- Disaster recovery

### CI/CD Pipeline
1. **Test:** Unit, integration, E2E tests
2. **Build:** Docker image creation
3. **Deploy:** Staging then production
4. **Monitor:** Health checks and metrics

## Future Enhancements

### Short-term (Sprint 2-3)
- Video upload functionality
- Metadata handling
- Basic error recovery

### Medium-term (Sprint 4-5)
- Celery integration for async tasks
- Database for job tracking
- Advanced error handling

### Long-term (Sprint 6+)
- Multiple account support
- Advanced monitoring
- Machine learning for behavior simulation

## Decision Log

### Key Architecture Decisions

#### 1. Playwright over Graph API
**Decision:** Use browser automation instead of Instagram Graph API
**Reason:** Graph API doesn't support Reels upload for all accounts
**Trade-off:** More fragile (UI changes) but more capable

#### 2. Manual 2FA Input
**Decision:** Pause for manual 2FA code input
**Reason:** Automated 2FA requires SMS/email access or backup codes
**Trade-off:** Less automated but more secure and reliable

#### 3. Cookie Encryption Optional
**Decision:** Make encryption optional with environment key
**Reason:** Development convenience vs production security
**Trade-off:** Flexibility for different environments

#### 4. Async Architecture
**Decision:** Use async/await pattern throughout
**Reason:** Better performance for I/O operations
**Trade-off:** More complex code structure

## Compliance and Standards

### Code Standards
- **PEP 8:** Python style guide
- **Type Hints:** Full type annotation
- **Docstrings:** Google format
- **Testing:** 80%+ coverage required

### Security Standards
- **OWASP Top 10:** Compliance checked
- **Credential Handling:** Never in code
- **Data Encryption:** For sensitive information
- **Access Control:** Principle of least privilege

### Operational Standards
- **Logging:** Structured, searchable logs
- **Monitoring:** Health checks and metrics
- **Alerting:** Proactive failure detection
- **Backup:** Regular data backups

---

**Architecture Status:** ✅ Approved  
**Last Updated:** 2026-04-08  
**Architect:** Alex Technical Architect  
**Next Review:** 2026-04-15 or major feature addition