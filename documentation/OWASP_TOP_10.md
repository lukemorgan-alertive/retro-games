# OWASP Top 10 Security Analysis - Retro Games Web Application

## Executive Summary

This document provides a comprehensive security assessment of the Retro Games web application (FastAPI REST API + CLI tool) against the **OWASP Top 10 2021** vulnerabilities. The analysis covers both the API (`retro-games-api/`) and CLI (`retro-games-cli/`) components.

**Overall Security Rating: **NOT PRODUCTION-READY**

⚠️ **Critical Issues Identified:** While the application demonstrates excellent SQL injection prevention, it lacks mandatory security features including authentication, authorization, logging, and monitoring. Immediate remediation of A07 (Authentication Failures) and A09 (Logging/Monitoring) is required before any production deployment.

---

## OWASP Top 10 2021 Assessment

### A01:2021 - Broken Access Control
**Status: 🟡 NEEDS ATTENTION**

#### Current State
- ❌ **No authentication implemented** - API endpoints are completely open
- ❌ **No authorization** - Any user can read, modify, or delete any game
- ❌ **No rate limiting** - Vulnerable to abuse and DoS attacks
- ❌ **No CORS configuration** - Default CORS may be too permissive

#### Risks
- Unauthorized users can create, modify, or delete game records
- No audit trail of who performed what action
- No protection against automated abuse

#### Recommendations
```python
# 1. Add authentication middleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Security

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    # Implement JWT token verification
    pass

@app.post("/games", dependencies=[Depends(verify_token)])
async def create_game(game: GameCreate):
    ...

# 2. Add CORS with specific origins
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 3. Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/games")
@limiter.limit("10/minute")
async def create_game(request: Request, game: GameCreate):
    ...
```

---

### A02:2021 - Cryptographic Failures
**Status: 🟢 LOW RISK**

#### Current State
- ✅ No sensitive data (passwords, payment info, PII) stored
- ✅ SQLite database stores only game catalog information
- ⚠️ No HTTPS enforcement documented
- ⚠️ No encryption at rest for database file

#### Risks
- Database file accessible to anyone with filesystem access
- Data transmitted in plaintext if HTTPS not enforced

#### Recommendations
```python
# 1. Force HTTPS in production
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# 2. Add security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# 3. Consider SQLCipher for sensitive deployments
# pip install sqlcipher3
# Use encrypted database for production
```

---

### A03:2021 - Injection
**Status: 🟢 EXCELLENT**

#### Current State
- ✅ **All database queries use parameterized statements**
- ✅ Proper use of `?` placeholders in SQLite
- ✅ No string concatenation or f-strings in SQL
- ✅ Input validation via Pydantic models
- ✅ Database constraints enforce data integrity

#### Security Implementation
```python
# ✓ SAFE - Parameterized query in models.py
cursor = conn.execute(
    "INSERT INTO games (title, release_year, platform, date_acquired, condition) VALUES (?, ?, ?, ?, ?)",
    (title, release_year, platform, date_acquired.isoformat(), condition)
)

# ✓ SAFE - Pydantic validation in app.py
class GameCreate(BaseModel):
    title: str = Field(..., min_length=1)
    release_year: int = Field(..., ge=1970, le=2030)
    condition: Optional[Literal['mint', 'vgc', 'gc', 'used']] = None
```

#### Verification
See detailed analysis in [SECURITY.md](SECURITY.md) for comprehensive SQL injection prevention review.

**No action required** - Implementation follows OWASP best practices.

---

### A04:2021 - Insecure Design
**Status: 🟡 NEEDS ATTENTION**

#### Current State
- ⚠️ No input validation limits (title length, platform values)
- ⚠️ No business logic constraints (duplicate detection)
- ⚠️ No pagination for list endpoints
- ⚠️ Error messages may leak implementation details

#### Risks
- Unbounded queries can cause performance issues
- Large inputs can cause resource exhaustion
- No protection against duplicate entries

#### Recommendations
```python
# 1. Add pagination
from fastapi import Query

@app.get("/games")
async def list_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    games = GameModel.get_all(skip=skip, limit=limit)
    return games

# 2. Add field length limits
class GameCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    platform: str = Field(..., min_length=1, max_length=50)
    ...

# 3. Add duplicate detection
@staticmethod
def exists(title: str, platform: str, release_year: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM games WHERE title = ? AND platform = ? AND release_year = ?",
            (title, platform, release_year)
        )
        return cursor.fetchone()[0] > 0

# 4. Generic error messages
try:
    game_id = GameModel.create(...)
except Exception as e:
    logger.error(f"Database error: {e}")  # Log detailed error
    raise HTTPException(status_code=500, detail="Internal server error")  # Generic message
```

---

### A05:2021 - Security Misconfiguration
**Status: 🟡 NEEDS ATTENTION**

#### Current State
- ⚠️ Default FastAPI error pages (leak stack traces in debug mode)
- ⚠️ No security headers configured
- ✅ Database path properly configured outside web root
- ⚠️ No documented production deployment configuration

#### Risks
- Debug mode in production exposes stack traces
- Missing security headers allow various attacks
- No hardening guidance provided

#### Recommendations
```python
# 1. Disable debug mode in production
import os

app = FastAPI(
    title="Retro Games API",
    debug=os.getenv("ENVIRONMENT") != "production"
)

# 2. Custom exception handler
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data"}  # Don't expose validation details
    )

# 3. Environment-based configuration
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    database_path: str = "./retro_games.db"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()

# 4. Create production deployment guide
# - Disable debug mode
# - Use proper WSGI server (Gunicorn)
# - Set up HTTPS
# - Configure firewall
# - Set restrictive file permissions on database
```

---

### A06:2021 - Vulnerable and Outdated Components
**Status: 🟡 NEEDS ATTENTION**

#### Current State
- ⚠️ No dependency version pinning in requirements.txt
- ⚠️ No security scanning configured
- ⚠️ No update policy documented

#### Current Dependencies
```
retro-games-api/requirements.txt:
- fastapi
- uvicorn[standard]
- pydantic
```

#### Risks
- Installing latest versions may introduce breaking changes or vulnerabilities
- No mechanism to detect vulnerable dependencies

#### Recommendations
```bash
# 1. Pin exact versions
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0

# 2. Add security scanning
pip install safety pip-audit

# Add to CI/CD pipeline
safety check
pip-audit

# 3. Regular dependency updates
# Create dependabot.yml or renovate.json
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/retro-games-api"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

# 4. Add vulnerability scanning to README
# Document security update process
```

---

### A07:2021 - Identification and Authentication Failures
**Status: 🔴 CRITICAL**

#### Current State
- ❌ **No authentication implemented**
- ❌ No user accounts or session management
- ❌ No password policies (N/A - no users)
- ❌ No multi-factor authentication

#### Risks
- **CRITICAL**: Anyone can access all API endpoints
- No way to identify who performed actions
- No audit trail for compliance

#### Recommendations
```python
# 1. Implement JWT authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY")  # Generate strong secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify user credentials against database
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 2. Protect endpoints
@app.post("/games", dependencies=[Depends(get_current_user)])
async def create_game(game: GameCreate):
    ...

# 3. Add user table to database
"""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);
"""
```

---

### A08:2021 - Software and Data Integrity Failures
**Status: 🟡 NEEDS ATTENTION**

#### Current State
- ⚠️ No integrity verification for CSV imports
- ⚠️ No validation of data sources
- ⚠️ No CI/CD pipeline documented
- ⚠️ No code signing or package verification

#### Risks
- Malicious CSV files could inject unexpected data
- No guarantee of code integrity in deployment
- Dependency tampering possible

#### Recommendations
```python
# 1. Validate CSV imports
import csv
from io import StringIO

def validate_csv_structure(csv_content: str) -> bool:
    """Validate CSV has expected columns and format."""
    try:
        reader = csv.DictReader(StringIO(csv_content))
        required_fields = {'title', 'release_year', 'platform', 'date_acquired'}
        
        if not required_fields.issubset(set(reader.fieldnames)):
            return False
        
        # Validate each row
        for row in reader:
            if not row['title'] or not row['platform']:
                return False
            try:
                int(row['release_year'])
                date.fromisoformat(row['date_acquired'])
            except (ValueError, KeyError):
                return False
        return True
    except Exception:
        return False

# 2. Add file size limits
from fastapi import File, UploadFile

@app.post("/import")
async def import_games(file: UploadFile = File(...)):
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    if not validate_csv_structure(contents.decode()):
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    
    # Process file
    ...

# 3. Add integrity checks to CI/CD
# GitHub Actions example
"""
- name: Verify dependencies
  run: |
    pip install pip-audit
    pip-audit --require-hashes -r requirements.txt
    
- name: Run security checks
  run: |
    pip install bandit
    bandit -r . -f json -o bandit-report.json
"""

# 4. Pin dependencies with hashes
# pip freeze --all > requirements.txt
# pip-compile --generate-hashes requirements.in
```

---

### A09:2021 - Security Logging and Monitoring Failures
**Status: 🔴 CRITICAL**

#### Current State
- ❌ **No logging implemented**
- ❌ No monitoring or alerting
- ❌ No audit trail for database changes
- ❌ No error tracking

#### Risks
- Cannot detect security incidents
- No forensic capability after breach
- Cannot track unauthorized access attempts
- No visibility into application health

#### Recommendations
```python
# 1. Implement comprehensive logging
import logging
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retro_games_api")

handler = RotatingFileHandler(
    "api_logs.log",
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# 2. Log security-relevant events
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.utcnow()
    
    logger.info({
        "event": "request_started",
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent")
    })
    
    response = await call_next(request)
    
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info({
        "event": "request_completed",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_seconds": duration
    })
    
    return response

# 3. Log database operations
class GameModel:
    @staticmethod
    def create(title: str, release_year: int, platform: str, 
               date_acquired: date, condition: Optional[str] = None) -> int:
        try:
            with get_db_connection() as conn:
                cursor = conn.execute(...)
                conn.commit()
                game_id = cursor.lastrowid
                
                logger.info({
                    "event": "game_created",
                    "game_id": game_id,
                    "title": title,
                    "platform": platform
                })
                
                return game_id
        except Exception as e:
            logger.error({
                "event": "game_creation_failed",
                "error": str(e),
                "title": title
            })
            raise

    @staticmethod
    def delete(game_id: int) -> bool:
        # Log before deletion for audit trail
        game = GameModel.get_by_id(game_id)
        if game:
            logger.warning({
                "event": "game_deleted",
                "game_id": game_id,
                "game_data": game
            })
        ...

# 4. Add monitoring endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# 5. Failed authentication attempts logging
def log_failed_login(username: str, ip_address: str):
    logger.warning({
        "event": "failed_login_attempt",
        "username": username,
        "ip_address": ip_address,
        "timestamp": datetime.utcnow().isoformat()
    })

# 6. Set up alerting (example with email)
from email.mime.text import MIMEText
import smtplib

def send_alert(subject: str, message: str):
    """Send security alert email."""
    if os.getenv("ENVIRONMENT") == "production":
        msg = MIMEText(message)
        msg['Subject'] = f"[SECURITY ALERT] {subject}"
        msg['From'] = os.getenv("ALERT_FROM_EMAIL")
        msg['To'] = os.getenv("ALERT_TO_EMAIL")
        
        with smtplib.SMTP(os.getenv("SMTP_SERVER")) as server:
            server.send_message(msg)
```

---

### A10:2021 - Server-Side Request Forgery (SSRF)
**Status: 🟢 LOW RISK**

#### Current State
- ✅ No external URL fetching functionality
- ✅ No user-provided URLs processed
- ✅ No webhook or callback features
- ✅ No image/file fetching from URLs

#### Risks
- Minimal SSRF risk with current functionality

#### Recommendations
```python
# If adding URL processing in the future:

# 1. Whitelist allowed domains
ALLOWED_DOMAINS = ["api.allowed-service.com"]

def validate_url(url: str) -> bool:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.hostname in ALLOWED_DOMAINS

# 2. Use explicit deny lists for internal networks
BLOCKED_IPS = [
    "127.0.0.0/8",      # Loopback
    "10.0.0.0/8",       # Private
    "172.16.0.0/12",    # Private
    "192.168.0.0/16",   # Private
    "169.254.0.0/16",   # Link-local
]

import ipaddress

def is_safe_ip(ip: str) -> bool:
    ip_obj = ipaddress.ip_address(ip)
    for blocked in BLOCKED_IPS:
        if ip_obj in ipaddress.ip_network(blocked):
            return False
    return True

# 3. If implementing CSV import from URL
@app.post("/import-from-url")
async def import_from_url(url: str):
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    # Use timeout and size limits
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url, follow_redirects=False)
        
        if len(response.content) > 10_000_000:  # 10MB
            raise HTTPException(status_code=413, detail="File too large")
        
        # Process content
        ...
```

---

## Priority Action Items

### 🔴 CRITICAL (Implement Immediately)
1. **Add Authentication** (A07) - No access control exists
2. **Implement Logging** (A09) - No visibility into security events
3. **Add Rate Limiting** (A01) - Prevent abuse and DoS

### 🟡 HIGH (Implement Soon)
4. **Add Security Headers** (A02, A05)
5. **Configure CORS Properly** (A01)
6. **Add Input Validation Limits** (A04)
7. **Pin Dependency Versions** (A06)
8. **Add Monitoring Endpoints** (A09)

### 🟢 MEDIUM (Consider for Future)
9. **Add Pagination** (A04)
10. **Implement CSV Validation** (A08)
11. **Set up Dependency Scanning** (A06)
12. **Add Production Deployment Guide** (A05)

---

## Security Testing Checklist

### Authentication Testing
- [ ] Test without credentials (should be rejected)
- [ ] Test with invalid tokens
- [ ] Test token expiration
- [ ] Test password policies (if implemented)

### Authorization Testing
- [ ] Verify users can only access their own resources
- [ ] Test privilege escalation attempts
- [ ] Verify CORS configuration

### Input Validation Testing
- [ ] Test with extremely long strings
- [ ] Test with special characters in all fields
- [ ] Test with negative numbers
- [ ] Test with future dates (year 9999)
- [ ] Test SQL injection payloads (already verified secure)

### API Security Testing
- [ ] Test rate limiting (should block after threshold)
- [ ] Test with missing required fields
- [ ] Test with invalid data types
- [ ] Test pagination limits
- [ ] Verify error messages don't leak info

### Infrastructure Testing
- [ ] Verify HTTPS is enforced
- [ ] Check security headers present
- [ ] Verify debug mode is off in production
- [ ] Test file permission on database
- [ ] Verify logging is working

---

## Compliance Considerations

### GDPR (if storing user data)
- Implement user consent mechanisms
- Add data export functionality
- Add data deletion functionality
- Document data retention policies

### SOC 2 (if applicable)
- Implement access controls
- Add comprehensive logging
- Document security policies
- Implement change management

### PCI DSS (not applicable)
- No payment card data handled

---

## Security Development Lifecycle

### Secure Coding Guidelines
1. Always use parameterized queries (already done ✅)
2. Validate all inputs at API boundary
3. Use Pydantic models for type safety
4. Implement least privilege access
5. Log security-relevant events
6. Never log sensitive data
7. Use environment variables for secrets
8. Keep dependencies updated

### Code Review Checklist
- [ ] Parameterized queries used for all database operations
- [ ] Input validation present for user inputs
- [ ] Authentication checks on protected endpoints
- [ ] Error handling doesn't leak sensitive info
- [ ] Security logging added for important operations
- [ ] No hardcoded secrets or credentials

### Security Testing Schedule
- **Weekly**: Dependency vulnerability scanning
- **Monthly**: Manual security review
- **Quarterly**: Full penetration testing
- **Annually**: Third-party security audit

---

## Additional Resources

### OWASP Resources
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

### FastAPI Security
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

### Python Security
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Bandit Security Linter](https://bandit.readthedocs.io/)

---

## Conclusion

The Retro Games application has **excellent SQL injection protection** (A03) but requires immediate attention for **authentication** (A07) and **logging** (A09). The application follows many security best practices but lacks essential production security features.

**Recommended Next Steps:**
1. Implement authentication system (JWT)
2. Add comprehensive logging
3. Configure rate limiting and CORS
4. Pin dependency versions
5. Add security headers
6. Set up monitoring and alerting

Once these improvements are implemented, the application will be production-ready from a security perspective.

---

**Document Version:** 1.0  
**Date:** 2026-01-17  
**Reviewed By:** AI Security Analysis  
**Next Review:** 2026-04-17
