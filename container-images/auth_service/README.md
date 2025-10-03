# 🔐 Microservicio de Autenticación con FastAPI

Este proyecto proporciona un microservicio de autenticación y gestión de usuarios listo para producción, empaquetado en Docker. Utiliza FastAPI para los endpoints, SQLAlchemy para la interacción con la base de datos PostgreSQL, y JWT para la gestión de sesiones.

## 🎯 Características Principales

-   **API Segura**: Construido con FastAPI, endpoints para registro, login, verificación de email, renovación de tokens y logout.
-   **Gestión de Sesiones Moderna**: Utiliza JSON Web Tokens (JWT) con access tokens de corta duración y refresh tokens de larga duración.
-   **Base de Datos Robusta**: Diseñado para funcionar con PostgreSQL, gestionado a través de SQLAlchemy y migraciones con Alembic.
-   **Listo para Desplegar**: Totalmente dockerizado para un despliegue consistente y sencillo en plataformas como Google Cloud Run.

## 🏁 Guía de Construcción y Ejecución

### Paso 1: Preparación
-   Asegúrate de tener Docker instalado y corriendo en tu máquina.

### Paso 2: Construcción de la Imagen Docker
-   Navega al directorio raíz del repositorio (`ingeniia_services/`).
-   Ejecuta el siguiente comando para construir la imagen. Reemplaza `1.0` con la versión deseada.

    ```bash
    docker build -t genia/auth-service:1.0 -f container-images/auth_service/Dockerfile .
    ```

### Paso 3: Ejecutar el Contenedor Docker
-   Una vez construida la imagen, levanta un contenedor. **Importante**: Este servicio necesita conectarse a una base de datos PostgreSQL. Para pruebas locales, asegúrate de que tu contenedor PostgreSQL esté corriendo y en la misma red de Docker.

    ```bash
    # Ejemplo de ejecución (asegúrate de pasar las variables de entorno necesarias)
    docker run -d -p 8000:8080 \
      -e DATABASE_URL="postgresql+asyncpg://user:pass@host.docker.internal:5432/ingeniia_auth" \
      -e JWT_SECRET_KEY="tu-clave-secreta" \
      -e ENVIRONMENT="development" \
      --name auth-service \
      genia/auth-service:1.0
    ```
    *Nota: `host.docker.internal` es un alias especial de Docker para referirse a la máquina anfitriona (tu PC) desde dentro de un contenedor.*

### Paso 4: Verificar el Funcionamiento
-   Abre tu navegador y ve a la documentación interactiva de la API:

    ```
    http://localhost:8000/docs
    ```

## 📝 Cómo Usar la API
El flujo principal es `register` -> `verify-email` -> usar endpoints protegidos.

-   **Registrar un usuario (`POST /auth/register`)**:
    Usa la documentación interactiva o cURL para enviar los datos de un nuevo usuario.

    ```bash
    curl -X 'POST' \
      'http://localhost:8000/auth/register' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "username": "docker_user",
      "email": "docker@example.com",
      "password": "DockerUser123",
      "captcha_token": "test"
    }'
    ```
-   **Verificar el email (`POST /auth/verify-email`)**:
    Obtén el token de la base de datos (para pruebas locales) y envíalo a este endpoint para recibir tus tokens JWT.

-   **Acceder a rutas protegidas (`GET /auth/me`)**:
    Usa el `access_token` obtenido en el paso anterior en la cabecera `Authorization: Bearer <token>` para acceder a la información del usuario.

## ⚙️ Gestión del Contenedor
-   **Ver logs en tiempo real**:
    ```bash
    docker logs -f auth-service
    ```
-   **Detener y eliminar el contenedor**:
    ```bash
    docker stop auth-service && docker rm auth-service
    ```