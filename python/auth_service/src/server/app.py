import logging as log
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.auth import router as auth_router

def setup_logging():
    log.basicConfig(
        level=getattr(log, settings.LOG_LEVEL.upper(), log.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",)
    
    log.getLogger("sqlalchemy.engine.Engine").setLevel(log.WARNING)

setup_logging()
log = log.getLogger(__name__)

app = FastAPI(
    title="API de Autenticación - inGeniia",
    description="Microservicio de autenticación y gestión de usuarios",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/", include_in_schema=False)
async def root():
    """Redirige a la documentación"""
    return RedirectResponse(url="/docs")


@app.get("/healthz", tags=["Health"])
async def health_check():
    """Verifica que el servicio esté vivo"""
    return {"status": "ok", "service": "auth"}


app.include_router(auth_router)
app.include_router(auth_router, prefix="/auth")