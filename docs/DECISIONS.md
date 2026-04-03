# Decision Log

> **Note:** For open questions on architecture and data model, see [../TODO.md](../TODO.md).

## Deployment Runtime (Active)

- Application runtime: Docker container on Railway (Flask + gunicorn)
- Database: MySQL 8.0 on Railway (managed service)
- Previous cloud target (AWS CDK) explicitly removed on 2026-04-03
