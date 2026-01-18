# NorthFlow Production Roadmap

## Overview

This document tracks the transition of NorthFlow from a
database course project to a production-ready web application. Focus
areas include security, testing, infrastructure, and best practices.

**Current Deployment**: NorthFlow is already deployed to Railway with
a MySQL 8.0 database instance. See [DEPLOYMENT.md](DEPLOYMENT.md)
for current infrastructure details, environment setup, and rollback procedures.

---

## UX & User Perspective Shift

- [ ] **0. Shift from admin-view to single-user perspective**
  - **PRIORITY:** Do this before authentication
  - Current state: App shows all users, requires selecting user in dropdowns
  - Desired state: Each user sees only their own data
  - **Implementation steps:**
    1. Add "current user" concept (hardcoded user ID in session for now, will become authenticated user later)
    2. Remove user selection dropdowns from all pages (Questions, Check-ins, Summary)
    3. Update all routes to automatically filter by current user
    4. Change UI language: "Select a user" → "My Questions", "My Check-ins", "My Summary"
    5. Update questions page: Only show current user's questions, hide user column
    6. Update check-ins page: Only show current user's check-ins automatically
    7. Update summary page: Only show current user's summary data
    8. Simplify data access layer calls to always include current user context
    9. Add user switcher in dev mode (temporary, for testing different user views)
    10. When authentication is implemented, replace hardcoded user with `session['user_id']` from auth
  - **Files to update:**
    - `app/routes/main.py` - Add `_get_current_user()` helper, update all routes
    - `app/templates/questions.html` - Remove user dropdown, update language
    - `app/templates/checkins.html` - Remove user dropdown, auto-load user's check-ins
    - `app/templates/summary.html` - Remove user filter (or make it admin-only later)
    - `app/templates/base.html` - Update nav language to reflect "my" perspective
  - **Benefits:**
    - Clearer UX aligned with production use case
    - Data isolation ready for multi-tenant auth
    - Simplified user flows (no selection needed)
    - Natural transition to authenticated sessions

---

## Security (Items 1–5, 10)

- [x] **1. Audit security vulnerabilities**
  - ✅ COMPLETED: Comprehensive security audit performed
  - ✅ Identified 8 vulnerabilities (4 high priority, 3 medium priority)
  - ✅ Documented in `.agent/SECURITY_AUDIT.md` with detailed findings
  - ✅ All high/medium priority issues addressed in items 2-5

- [x] **2. Implement secrets management**
  - ✅ COMPLETED: Removed all hardcoded secrets
  - ✅ SECRET_KEY now required from environment (fails fast if missing)
  - ✅ All DB credentials loaded from .env file
  - ✅ Startup validation ensures SECRET_KEY exists
  - ✅ Generation command documented in README.md

- [x] **3. Add CSRF protection**
  - ✅ COMPLETED: Flask-WTF 1.2.2 integrated
  - ✅ CSRF tokens added to 50+ form fields across 3 templates
  - ✅ Global CSRF protection enabled in app initialization
  - ✅ Invalid CSRF requests return 400 error
  - ✅ All forms tested and working

- [ ] **4. Implement proper authentication**
  - Replace DB credential login gate with user-based auth
  - Add user registration, password hashing (bcrypt), session management
  - Implement password reset flow
  - Add email verification (optional but recommended)
  - **Note**: Comprehensive error handling completed (structured logging + generic user messages)

- [x] **5. Add input validation and sanitization**
  - ✅ COMPLETED: Marshmallow 4.2.0 integrated for validation
  - ✅ Created 5 validation schemas (Question, Checkin, Answer, SummaryFilter)
  - ✅ All POST endpoints validate input before database operations
  - ✅ Validation errors return user-friendly messages
  - ✅ Cleaned data prevents injection attacks

- [x] **10. Implement rate limiting**
  - ✅ COMPLETED: Flask-Limiter 3.5.0 integrated
  - ✅ Rate limits applied to 8 sensitive POST endpoints
  - ✅ 10 requests/minute on create/update/delete operations
  - ✅ IP-based rate limiting with 200 requests/hour global default
  - ✅ Returns HTTP 429 when limit exceeded

### Bonus Security Items Completed

- [x] **SQL Injection Prevention Verification**
  - ✅ COMPLETED: Comprehensive audit of all database operations
  - ✅ Verified all DAL uses stored procedures with safe parameter binding
  - ✅ Confirmed parameterized queries for any raw SQL
  - ✅ Raw SQL disabled by default (allow_raw_sql=False)
  - ✅ Tested against 6+ OWASP SQL injection payloads
  - ✅ Created test suite: `tests/test_sql_injection.py` (4 tests, all passing)
  - ✅ Documented in `.agent/SECURITY_ITEMS_5_AND_10.md`
  - **Result**: NO SQL INJECTION VULNERABILITIES FOUND

- [x] **HTTP Security Headers**
  - ✅ COMPLETED: Added security headers middleware
  - ✅ X-Content-Type-Options: nosniff
  - ✅ X-Frame-Options: DENY (prevents clickjacking)
  - ✅ X-XSS-Protection: 1; mode=block
  - ✅ Referrer-Policy: strict-origin-when-cross-origin
  - ✅ Content-Security-Policy configured

- [x] **Comprehensive Error Handling**
  - ✅ COMPLETED: Structured logging throughout application
  - ✅ Generic error messages shown to users (no sensitive details)
  - ✅ Detailed server-side logging with exc_info=True
  - ✅ All routes wrapped in try/except with proper logging

- [x] **Secure Configuration**
  - ✅ COMPLETED: Hardened Flask configuration
  - ✅ SESSION_COOKIE_SECURE=True in production
  - ✅ SESSION_COOKIE_HTTPONLY=True (prevents JS access)
  - ✅ SESSION_COOKIE_SAMESITE="Lax" (CSRF protection)
  - ✅ PERMANENT_SESSION_LIFETIME=3600 (1 hour timeout)

---

## Database & Data (Items 6, 11, 16, 17, 21, 27)

- [ ] **6. Implement database connection pooling**
  - Replace single connection pattern with connection pooling
  - Use mysql-connector-python pool or SQLAlchemy
  - Improve DAL to manage pool lifecycle
  - Reduce connection overhead

- [ ] **11. Add database migrations**
  - Setup Alembic or Flask-Migrate for schema versioning
  - Make schema changes reversible
  - Document migration procedures
  - Remove direct schema.sql dependency

- [ ] **16. Optimize database queries**
  - Profile slow queries
  - Add indexes where needed
  - Optimize stored procedures
  - Add query caching where appropriate
  - Ensure N+1 queries are eliminated

- [ ] **17. Implement pagination**
  - Add pagination to list endpoints (questions, checkins, summary)
  - Add limit/offset or cursor-based pagination
  - Update UI to handle pagination

- [ ] **21. Setup backup and recovery**
  - Implement automated database backups
  - Test recovery procedures
  - Document backup/restore steps
  - Plan RTO/RPO requirements for data loss scenarios

- [x] **27. Remove seed data from schema file**
  - ✅ COMPLETED: Removed 8 test users and 719 lines of seed data
  - ✅ Schema reduced from 1095 lines to 377 lines
  - ✅ Kept only Demo User (ID 1) for bootstrapping the app
  - ✅ All stored procedures, views, and table definitions intact
  - ✅ All tests passing with clean database
  - **Note**: Demo User will be removed when authentication is implemented (item 6)
  - **Next step**: After item 27 complete, prioritize security items (1-5, 10)

---

## Testing & Code Quality (Items 7, 14, 15)

- [ ] **7. Expand test suite**
  - Add unit tests for all service/DAL modules
  - Add integration tests for routes
  - Add end-to-end tests for critical user flows
  - Aim for >80% coverage
  - Add tests to CI/CD

- [ ] **14. Add type hints throughout**
  - Add type annotations to all Python functions
  - Add type annotations to module-level code
  - Add py.typed marker
  - Run mypy in CI/CD
  - Improves IDE support and catches bugs early

- [ ] **15. Improve API documentation**
  - Document all endpoints (method, path, params, response)
  - Add OpenAPI/Swagger spec
  - Generate interactive API docs
  - Add docstrings to all functions

---

## Logging & Monitoring (Items 8, 9, 22)

- [ ] **8. Add comprehensive logging**
  - Implement structured logging throughout app (debug, info, warning, error levels)
  - Log security events, DB errors, API requests
  - Use rotating file handler or centralized logging

- [ ] **9. Setup error handling and monitoring**
  - Add custom error pages (400, 403, 404, 500)
  - Implement error tracking (Sentry or similar)
  - Add health checks and readiness probes for orchestration

- [ ] **22. Add monitoring and alerting**
  - Setup application metrics (requests, errors, latency)
  - Setup infrastructure monitoring (CPU, memory, disk)
  - Configure alerts for critical issues
  - Use Prometheus/Grafana or similar

---

## Deployment & Infrastructure (Items 12, 13, 23, 25)

- [ ] **12. Dockerize application**
  - Create Dockerfile for app and docker-compose.yml for local dev with MySQL
  - Add multi-stage builds for production image
  - Include health checks

- [ ] **13. Setup CI/CD pipeline**
  - Create GitHub Actions workflow for linting, testing, building, deploying
  - Run security checks in pipeline
  - Enforce standards before merge
  - Deploy to staging/prod on success

- [ ] **23. Create deployment guide**
  - Document production deployment steps
  - Include prerequisites, configuration, security setup
  - Add runbooks for common operations (scale, rollback, maintenance)

- [ ] **25. Setup environment-specific configs**
  - Create separate configs for dev, staging, and production
  - Use feature flags for gradual rollouts
  - Document environment differences and setup procedures

---

## Frontend & UX (Items 18, 19, 20)

- [ ] **18. Add asset optimization**
  - Minify CSS and JS
  - Add cache busting
  - Implement lazy loading for images
  - Use CDN for static assets in production
  - Add compression (gzip)

- [ ] **19. Improve responsive design**
  - Audit all templates for mobile compatibility
  - Improve CSS media queries
  - Test on multiple devices
  - Ensure touch-friendly interface
  - Add mobile-first approach

- [ ] **20. Add accessibility (WCAG)**
  - Audit for WCAG 2.1 AA compliance
  - Add ARIA labels
  - Ensure keyboard navigation
  - Test with screen readers
  - Add alt text to images
  - Fix color contrast issues

---

## Compliance & Legal (Item 24)

- [ ] **24. Add privacy and legal docs**
  - Create Privacy Policy, Terms of Service, and Cookie Policy
  - Ensure GDPR compliance (if applicable)
  - Document data retention policies
  - Add consent mechanisms

---

## Suggested Priority Order

**Phase 1 (Foundation): ✅ MOSTLY COMPLETE**
~~1, 2, 3, 5, 10~~ ✅ **DONE** — Security items completed
(CSRF, input validation, rate limiting, secrets management,
error handling, SQL injection verification)  
4 — Authentication (in progress) — Only remaining Phase 1 item

**Phase 2 (Stability):**
7, 14, 15 — Testing and code quality; enables confident refactoring.

**Phase 3 (Infrastructure):**
12, 13, 23, 25 — Docker + CI/CD + deployment; unlocks faster iteration.

**Phase 4 (Optimization):**
6, 8, 9, 11, 16, 17, 18, 19, 20, 21, 22, 24 — Performance, monitoring, UX, compliance.

---

## Current Status Summary

**Completed (9 items):**
- ✅ Item 1: Security Audit
- ✅ Item 2: Secrets Management
- ✅ Item 3: CSRF Protection
- ✅ Item 5: Input Validation & Sanitization
- ✅ Item 10: Rate Limiting
- ✅ Item 27: Remove Seed Data
- ✅ Bonus: SQL Injection Prevention Verification
- ✅ Bonus: HTTP Security Headers
- ✅ Bonus: Comprehensive Error Handling & Logging
- ✅ Bonus: Secure Session Configuration

**In Progress:**
- 🔄 Item 4: User Authentication (comprehensive error handling done, auth system pending)

**Next Priorities:**
1. Item 4: Complete user authentication system
2. Item 7: Expand test suite (currently 9 tests passing)
3. Items 8-9: Enhanced logging and monitoring

**Test Status:** 9/9 tests passing ✅  
**Linting Status:** All checks passing ✅  
**Dependencies Added:** Flask-WTF, marshmallow, Flask-Limiter
