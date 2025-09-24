from typing import Optional
from pydantic import BaseModel

class Whiteboard(BaseModel):
    """Define la estructura de los datos de una pizarra."""
    id: str
    preview_url: str # URL de la imagen de previsualización
    file_url: str    # URL para descargar el archivo .excalidraw

class Video(BaseModel):
    """Define la estructura de los datos de un video."""
    id: str
    title: str
    description: str
    youtube_id: str
    duration_minutes: int
    thumbnail_url: str
    whiteboard: Optional[Whiteboard] = None
    
class CodeSnippet(BaseModel):
    """Define la estructura de un fragmento de código."""
    id: str
    title: str
    language: str
    github_url: str
    code: str