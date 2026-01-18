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
  - **PRIORITY: Do this before authentication**
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

- [ ] **1. Audit security vulnerabilities**
  - Review code for SQL injection, XSS, CSRF, hardcoded secrets, insecure defaults
  - Check password handling, session management, and input validation
  - Document findings and categorize by severity

- [ ] **2. Implement secrets management**
  - Remove hardcoded secrets from codebase
  - Use environment variables for all sensitive config (DB creds, SECRET_KEY, API keys)
  - Add validation that required secrets exist on startup

- [ ] **3. Add CSRF protection**
  - Integrate Flask-WTF or similar for CSRF token generation/validation
  - Ensure tokens are present in all form submissions
  - Test with real form submissions

- [ ] **4. Implement proper authentication**
  - Replace DB credential login gate with user-based auth
  - Add user registration, password hashing (bcrypt), session management
  - Implement password reset flow
  - Add email verification (optional but recommended)

- [ ] **5. Add input validation and sanitization**
  - Validate all user inputs on both client and server side
  - Use Flask-Inputs or similar for robust validation
  - Sanitize HTML/SQL inputs to prevent injection attacks

- [ ] **10. Implement rate limiting**
  - Add rate limiting to prevent abuse (login, API endpoints)
  - Use Flask-Limiter or similar
  - Implement IP-based and/or user-based rate limits

---

## Database & Data (Items 6, 11, 16, 17, 21)

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

**Phase 1 (Foundation):**
1, 2, 3, 4, 5, 10 — Security first; cannot be production-ready without it.

**Phase 2 (Stability):**
7, 14, 15 — Testing and code quality; enables confident refactoring.

**Phase 3 (Infrastructure):**
12, 13, 23, 25 — Docker + CI/CD + deployment; unlocks faster iteration.

**Phase 4 (Optimization):**
6, 8, 9, 11, 16, 17, 18, 19, 20, 21, 22, 24 — Performance, monitoring, UX, compliance.
