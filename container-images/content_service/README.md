# 🎬 Microservicio de Contenido con FastAPI

Este microservicio gestiona y sirve los metadatos del contenido educativo de la plataforma, como la información de los videos.

## 🎯 Características Principales

- **API Centralizada**: Provee un punto de acceso único para todo el contenido didáctico.
- **Ligero y Rápido**: Construido con FastAPI para una alta performance.
- **Basado en Archivos**: Utiliza un archivo `videos.json` como fuente de datos, facilitando la adición de contenido sin necesidad de una base de datos compleja al inicio.
- **Listo para Desplegar**: Totalmente dockerizado para un despliegue rápido y consistente.

## 🏁 Guía de Construcción y Despliegue

### Paso 1: Construcción de la Imagen Docker
Navega al directorio raíz `ingeniia_services/` y ejecuta el siguiente comando:

```bash
docker build -t ingeniia/content-service:1.0 -f container-images/content_service/Dockerfile .
```

### Paso 2: Ejecutar el Contenedor Docker
Una vez construida la imagen, levanta un contenedor. Usaremos el puerto `8001` para no chocar con el servicio de `credit-scoring`.

```bash
docker run -d -p 8001:8000 --name content-service ingeniia/content-service:1.0
```

### Paso 3: Verificar el Funcionamiento
Abre tu navegador y ve a la documentación interactiva de la API:

```bash
http://localhost:8001/docs
```

## 📝 Cómo Usar la API

La API expone varios endpoints para acceder a los diferentes tipos de contenido.
### Endpoint:  `GET /videos/topic/{topic_name}`.

Recupera la lista de videos y sus pizarras asociadas para un tema específico (ej. mlp, cnn).

#### Ejemplo: Usando cURL

```bash
curl -X 'GET' 'http://localhost:8001/videos/topic/mlp' -H 'accept: application/json'
```

#### Respuesta Exitosa Esperada (200 OK)

Recibirás una lista de videos en formato JSON:

```json
[
  {
    "id": "mlp001",
    "title": "Introducción y Entorno de Desarrollo",
    "description": "...",
    "youtube_id": "GnqEYBuBM9E",
    "duration_minutes": 51,
    "thumbnail_url": "/images/thumbnails/mlp_01.png",
    "whiteboard": {
      "id": "mlp001_wb",
      "preview_url": "/images/whiteboards/mlp_wb_01.png",
      "file_url": "/whiteboards/mlp_01_introduccion.excalidraw"
    }
  }
]
```

#### Respuesta de Error (404 Not Found)

Si pides un tema que no existe (ej. `rnn`):

```json
{
  "detail": "El tema 'rnn' no fue encontrado."
}
```

### Endpoint:  `GET /snippets/topic/{topic_name}`.

Recupera los fragmentos de código relevantes para un tema específico.

#### Ejemplo: Usando cURL

```bash
curl -X 'GET' 'http://localhost:8001/snippets/topic/mlp' -H 'accept: application/json'
```

#### Respuesta Exitosa Esperada (200 OK)

Recibirás una lista de videos en formato JSON:

```json
[
  {
    "id": "mlp_snip_01",
    "title": "Definiendo la Arquitectura",
    "language": "python",
    "github_url": "https://github.com/tu-usuario/ingeniia_services/blob/main/python/credit_scoring/src/training/model.py",
    "code": "import torch\nimport torch.nn as nn\n# ..."
  },
  {
    "id": "mlp_snip_02",
    "title": "Orquestando el Entrenamiento",
    "language": "python",
    "github_url": "https://github.com/tu-usuario/ingeniia_services/blob/main/python/credit_scoring/src/training/train.py",
    "code": "\"\"\"\nTraining Module for Credit Scoring MLP\n\"\"\"\n# ..."
  }
]
```

#### Respuesta de Error (404 Not Found)

Si pides un tema que no existe (ej. `rnn`):

```json
{
  "detail": "El tema 'rnn' no fue encontrado."
}
```

## ⚙️ Gestión del Contenedor
Aquí tienes algunos comandos útiles para administrar el contenedor Docker.

- Puedes detener el contenedor en cualquier momento usando:

    ```bash
    docker stop content-service
    ```

- Ver los logs en tiempo real:
    ```bash
    docker logs -f content-service 
    ```

- Reiniciar un contenedor detenido::
    ```bash
    docker start content-service  
    ```

- Reiniciar un contenedor detenido::
    ```bash
    docker stop content-service  && docker rm content-service