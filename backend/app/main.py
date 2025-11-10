from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import auth, patients, appointments, billing, ai, gdpr, prescriptions, lab_results, hospital_settings, users, financial, ai_chat
from app.core.security_headers import SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Healthcare automation system with offline-first capabilities",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (security)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.mediflow.com", "mediflow.com"]
    )

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if settings.is_production else str(exc)
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    init_db()
    logger.info("Application startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation disabled in production"
    }


# Include routers
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.api_v1_prefix}/users", tags=["User Management"])
app.include_router(patients.router, prefix=f"{settings.api_v1_prefix}/patients", tags=["Patients"])
app.include_router(appointments.router, prefix=f"{settings.api_v1_prefix}/appointments", tags=["Appointments"])
app.include_router(billing.router, prefix=f"{settings.api_v1_prefix}/billing", tags=["Billing"])
app.include_router(financial.router, prefix=f"{settings.api_v1_prefix}/financial", tags=["Financial Management"])
app.include_router(prescriptions.router, prefix=f"{settings.api_v1_prefix}/prescriptions", tags=["E-Prescriptions"])
app.include_router(lab_results.router, prefix=f"{settings.api_v1_prefix}/lab-results", tags=["Lab Results"])
app.include_router(hospital_settings.router, prefix=f"{settings.api_v1_prefix}/hospital-settings", tags=["Hospital Settings"])
app.include_router(ai.router, prefix=f"{settings.api_v1_prefix}/ai", tags=["AI"])
app.include_router(ai_chat.router, prefix=f"{settings.api_v1_prefix}", tags=["AI Chat Assistant"])
app.include_router(gdpr.router, prefix=f"{settings.api_v1_prefix}/gdpr", tags=["GDPR Compliance"])
