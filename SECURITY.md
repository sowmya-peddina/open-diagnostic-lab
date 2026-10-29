# Security

## Supported deployment model

Self-hosted Docker Compose with PostgreSQL on a private network. The database port is **not** published to the host by default.

## Baseline hardening

1. Copy `.env.example` to `.env` and change `SECRET_KEY`, `POSTGRES_PASSWORD`, and `ADMIN_PASSWORD` before storing real patient data.
2. Put the `web` service behind TLS (see `deploy/Caddyfile.example`). Set `COOKIE_SECURE=true` when using HTTPS.
3. Limit who can reach port `WEB_PORT` (firewall / VPN).
4. Create individual staff accounts; do not share the default admin password.
5. Keep regular encrypted backups (`scripts/backup.sh`) offline or in clinic-controlled storage.

## Authentication

- Session cookies are HTTP-only (`odl_session`).
- Passwords are hashed with bcrypt.
- Admin-only endpoints guard user creation, clinic settings, doctor/test catalog writes.

## Reporting vulnerabilities

Please open a private security advisory or email the repository maintainers. Do not file public issues that expose exploit details for unpatched releases.

## Out of scope for MVP

- Multi-tenant SaaS isolation
- Formal HIPAA/DISHA certification
- Hardware security modules / field-level encryption beyond host disk encryption
- External identity providers (OIDC/SAML)
