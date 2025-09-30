# python/content_service/src/server/app.py
import os
import json
import logging as log
from typing import List

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from src.server.schemas import Video, CodeSnippet

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")



# --- Carga de datos al iniciar ---
CONTENT_DATA = {}
try:
    # Construye la ruta al archivo de datos de forma robusta
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'content.json')
    with open(data_path, 'r') as f:
        CONTENT_DATA = json.load(f)
    log.info("Archivo de videos cargado exitosamente.")
except FileNotFoundError:
    log.error("Error crítico: No se encontró el archivo 'videos.json'.")
except json.JSONDecodeError:
    log.error("Error crítico: El archivo 'content.json' no es un JSON válido.")

# --- Inicialización de FastAPI ---
app = FastAPI(
    title="API de Contenido Educativo",
    description="Un microservicio para servir metadatos de videos y otros contenidos de la plataforma.",
    version="1.0.0"
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://ingeniia.co",
    "https://www.ingeniia.co",
    "https://api.ingeniia.co",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints de la API ---
@app.get("/", include_in_schema=False)
async def root():
    """Redirige a la documentación interactiva de la API."""
    return RedirectResponse(url="/docs")

# router versionado
v1 = APIRouter(prefix="/v1", tags=["Contenido"])

@v1.get("/healthz", tags=["Health"])
async def healthz():
    return {"status": "ok"}

@v1.get("/videos/topic/{topic_name}", response_model=List[Video], tags=["Contenido"], summary="Obtiene la lista de videos para un tema específico")
async def get_videos_by_topic(topic_name: str) -> List[Video]:
    """
    Recupera una lista de videos filtrada por el tema de la red neuronal.

    - **topic_name**: El identificador del tema (ej. 'mlp', 'cnn').
    - **Respuesta**: Una lista de objetos de video correspondientes a ese tema.
    """
    log.info(f"Solicitud de video para el tema: {topic_name}")
    videos = CONTENT_DATA.get(topic_name)

    if not videos:
        log.warning(f"No se encontraron videos para el tema: {topic_name}")
        raise HTTPException(
            status_code=404,
            detail=f"El tema '{topic_name}' no fue encontrado."
        )
    return videos


@v1.get("/snippets/topic/{topic_name}", response_model=List[CodeSnippet], tags=["Contenido"], summary="Obtiene la lista de snippets de código para un tema")
async def get_snippets_by_topic(topic_name: str) -> List[CodeSnippet]:
    """
    Recupera una lista de fragmentos de código para un tema específico.

    - **topic_name**: El identificador del tema (ej. 'mlp').
    - **Respuesta**: Una lista de objetos de snippets de código.
    """
    log.info(f"Solicitud de snippets para el tema: {topic_name}")
    snippets_data = CONTENT_DATA.get("code_snippets", {})
    snippets = snippets_data.get(topic_name)

    if not snippets:
        log.warning(f"No se encontraron snippets para el tema: {topic_name}")
        raise HTTPException(
            status_code=404,
            detail=f"Los snippets para el tema '{topic_name}' no fueron encontrados."
        )
    return snippets

app.include_router(v1)

@app.get("/healthz", include_in_schema=False, deprecated=True)
async def health_legacy(): return {"status": "ok"}

@app.get("/videos/topic/{topic_name}", include_in_schema=False, deprecated=True)
async def videos_legacy(topic_name: str): return await get_videos_by_topic(topic_name)

@app.get("/snippets/topic/{topic_name}", include_in_schema=False, deprecated=True)
async def snippets_legacy(topic_name: str): return await get_snippets_by_topic(topic_name)
