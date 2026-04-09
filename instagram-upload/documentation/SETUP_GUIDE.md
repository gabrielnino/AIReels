# Setup Guide - Instagram Upload Service

**Created by:** Jordan Documentation Specialist (Documentator)  
**Date:** 2026-04-08  
**Version:** 1.0

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Testing Setup](#testing-setup)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System:** Linux, macOS, or Windows
- **Python:** 3.8 or higher
- **RAM:** Minimum 4GB (8GB recommended)
- **Storage:** 1GB free space

### Software Requirements
1. **Python 3.8+**
   ```bash
   python3 --version
   ```
   
2. **Git** (for version control)
   ```bash
   git --version
   ```

3. **Chrome/Chromium Browser** (for Playwright automation)

## Installation Steps

### Step 1: Clone Repository
```bash
# Clone the AIReels repository
git clone https://github.com/your-org/AIReels.git
cd AIReels
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Navigate to instagram-upload module
cd instagram-upload

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 4: Configure Environment
```bash
# Copy environment template
cp .env.instagram.template .env.instagram

# Edit with your credentials
nano .env.instagram  # or use your preferred editor
```

## Configuration

### Environment Variables (.env.instagram)

**Required Configuration:**
```bash
# Instagram Credentials
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
INSTAGRAM_ENABLE_2FA=true  # Set to false if 2FA not enabled

# Playwright Configuration
PLAYWRIGHT_HEADLESS=false  # Set to true for CI/CD
PLAYWRIGHT_SLOW_MO=100     # Milliseconds between actions
PLAYWRIGHT_TIMEOUT=30000   # Timeout in milliseconds
```

**Optional Configuration:**
```bash
# Session Management
INSTAGRAM_COOKIES_PATH=./data/instagram_cookies.json
INSTAGRAM_SESSION_TIMEOUT=3600  # Session timeout in seconds

# Video Upload Settings
INSTAGRAM_MAX_VIDEO_SIZE_MB=100
INSTAGRAM_MAX_VIDEO_DURATION_SEC=90

# Security (Optional)
INSTAGRAM_ENCRYPTION_KEY=  # 32-byte key for cookie encryption
```

### Directory Structure Setup
```bash
# Create necessary directories
mkdir -p ./data ./logs ./logs/screenshots
mkdir -p ./videos/{to_upload,processed,failed}
```

## Testing Setup

### Install Testing Dependencies
```bash
# From instagram-upload directory
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

### Run Tests
```bash
# Run all tests
python run_tests.py

# Run unit tests only
python run_tests.py --unit

# Run with coverage report
python run_tests.py --coverage
```

### Test Structure
```
tests/
├── unit/                    # Unit tests
│   ├── auth/               # Authentication tests
│   │   ├── test_login_manager.py
│   │   ├── test_browser_service.py
│   │   └── test_cookie_manager.py
│   └── ...                 # Other unit tests
├── integration/            # Integration tests
└── e2e/                    # End-to-end tests
```

## Development Workflow

### Getting Started
1. **Checkout Development Branch**
   ```bash
   git checkout -b feature/instagram-upload
   ```

2. **Verify Installation**
   ```bash
   # Test basic import
   python -c "from src.auth.login_manager import InstagramLoginManager; print('Import successful')"
   ```

3. **Test Login Process**
   ```bash
   # Run login test (will pause for 2FA input if enabled)
   python scripts/test_instagram_login.py
   ```

### Code Quality Standards

**Pre-commit Hooks (Automatic Checks):**
- Tests must pass before commit
- Minimum 80% test coverage for new code
- Code must follow SOLID principles
- No duplicate code (DRY principle)

**Manual Checks:**
```bash
# Run code quality checks
python -m black src/ tests/      # Code formatting
python -m flake8 src/ tests/     # Linting
python -m mypy src/              # Type checking
```

## Troubleshooting

### Common Issues

#### 1. Playwright Installation Fails
**Symptoms:**
- `ModuleNotFoundError: No module named 'playwright'`
- Browser binaries not found

**Solutions:**
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright

# Install browsers with force
playwright install --force chromium

# Check installation
playwright --version
```

#### 2. Login Fails
**Symptoms:**
- "Invalid username/password" errors
- 2FA not working

**Solutions:**
1. **Verify Credentials:**
   ```bash
   cat .env.instagram | grep INSTAGRAM_USERNAME
   cat .env.instagram | grep INSTAGRAM_PASSWORD
   ```

2. **Test Manually in Browser:**
   - Open https://www.instagram.com
   - Try login with same credentials
   - Check if 2FA prompt appears

3. **Enable Debug Mode:**
   ```bash
   # Edit .env.instagram
   INSTAGRAM_DEBUG_MODE=true
   PLAYWRIGHT_HEADLESS=false  # See browser window
   ```

#### 3. 2FA Not Working
**Symptoms:**
- App doesn't pause for 2FA input
- "2FA code invalid" errors

**Solutions:**
1. **Check 2FA Configuration:**
   ```bash
   # Ensure 2FA is enabled in .env.instagram
   cat .env.instagram | grep INSTAGRAM_ENABLE_2FA
   # Should be: INSTAGRAM_ENABLE_2FA=true
   ```

2. **Manual 2FA Input:**
   - When app pauses, enter 6-digit code
   - Code must be exactly 6 digits
   - Code expires in 60 seconds

3. **Non-interactive Mode:**
   ```bash
   # Set 2FA code in environment
   export INSTAGRAM_2FA_CODE=123456
   # Or add to .env.instagram:
   # INSTAGRAM_2FA_CODE=123456
   ```

#### 4. Tests Fail
**Symptoms:**
- `ImportError` when running tests
- Mocking issues

**Solutions:**
```bash
# Run from project root
cd /home/luis/code/AIReels/instagram-upload

# Check Python path
python -c "import sys; print(sys.path)"

# Run individual test
python -m pytest tests/unit/auth/test_login_manager.py -v
```

### Logs and Debugging

#### Log Locations
- **Application Logs:** `./logs/instagram_automation.log`
- **Screenshots:** `./logs/screenshots/`
- **Cookie Storage:** `./data/instagram_cookies.json`
- **Session Info:** `./data/instagram_session.json`

#### Enable Debug Logging
```bash
# Edit .env.instagram
INSTAGRAM_DEBUG_MODE=true
PLAYWRIGHT_HEADLESS=false  # See what's happening
PLAYWRIGHT_SLOW_MO=500     # Slow down for observation
```

#### Generate Debug Information
```bash
# Create debug report
python -c "
import sys
sys.path.insert(0, '.')
try:
    from src.auth.login_manager import InstagramLoginManager
    print('✅ Login manager import successful')
    manager = InstagramLoginManager()
    print(f'✅ Manager created for user: {manager.username}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"
```

## Security Considerations

### Credential Safety
- **NEVER** commit `.env.instagram` to version control
- Use `.gitignore` to exclude sensitive files
- Rotate passwords regularly
- Use environment variables in production

### Session Management
- Cookies encrypted when encryption key provided
- Session timeout configurable
- Automatic cookie expiration handling
- Secure cookie storage with httpOnly and secure flags

### Production Deployment
1. **Separate Configuration:** Use environment variables or secrets manager
2. **Encryption:** Always set `INSTAGRAM_ENCRYPTION_KEY`
3. **Monitoring:** Enable health checks and alerts
4. **Backups:** Regular backup of configuration and data

## Next Steps

After successful setup:

1. **Test Complete Flow:**
   ```bash
   # Test login with cookies
   python scripts/test_instagram_login.py
   ```

2. **Review Code Structure:**
   - Browse `src/` directory
   - Review `tests/` structure
   - Check documentation

3. **Start Development:**
   - Refer to `START_DEVELOPMENT_PLAN.md`
   - Follow sprint planning
   - Attend daily standups

## Support

### Getting Help
- **Documentation:** Check this guide and README.md
- **Code Reference:** Review existing tests and examples
- **Team Communication:** Use Slack channel `#instagram-upload-dev`

### Reporting Issues
1. **Check Logs:** `tail -f logs/instagram_automation.log`
2. **Capture Screenshots:** Check `./logs/screenshots/`
3. **Create Issue:** Include error message and steps to reproduce

---

**Documentation Status:** ✅ Complete  
**Last Updated:** 2026-04-08  
**Maintained by:** Jordan Documentation Specialist  
**Next Review:** 2026-04-15