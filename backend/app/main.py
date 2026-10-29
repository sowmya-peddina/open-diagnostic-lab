from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import auth, doctors, orders, patients, reports, settings, tests, users
from app.core.config import get_settings

settings_cfg = get_settings()

app = FastAPI(
    title=settings_cfg.app_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

origins = [o.strip() for o in settings_cfg.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings_cfg.secret_key,
    session_cookie="odl_session",
    max_age=settings_cfg.session_max_age_seconds,
    same_site=settings_cfg.cookie_samesite,
    https_only=settings_cfg.cookie_secure,
)

app.include_router(auth.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")
app.include_router(tests.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
