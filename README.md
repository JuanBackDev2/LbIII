# GameVault API (Django REST Framework)

API REST para el proyecto GameVault. Usa Django, Django REST Framework, SQLite y JWT. Angular puede consumir los endpoints HTTP descritos abajo.

## 1. Instalación

Requiere Python 3.10+.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API local: `http://127.0.0.1:8000/api/`  
Panel de administración: `http://127.0.0.1:8000/admin/`

## 2. Endpoints

Todas las rutas salvo registro y login requieren el encabezado `Authorization: Bearer <access_token>`, excepto cuando se indica.

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/auth/registro/` | Crear cuenta |
| POST | `/api/auth/login/` | Iniciar sesión y recibir tokens |
| POST | `/api/auth/refresh/` | Renovar access token |
| POST | `/api/auth/logout/` | Invalidar refresh token |
| GET | `/api/juegos/` | Listar catálogo |
| GET | `/api/juegos/{id}/` | Ver juego |
| POST | `/api/juegos/` | Crear juego (solo staff) |
| PUT/PATCH | `/api/juegos/{id}/` | Editar juego (solo staff) |
| DELETE | `/api/juegos/{id}/` | Eliminar juego (solo staff) |
| GET | `/api/resenas/` | Listar reseñas |
| GET | `/api/resenas/{id}/` | Ver reseña |
| POST | `/api/resenas/` | Crear reseña como usuario autenticado |
| PUT/PATCH | `/api/resenas/{id}/` | Editar solo la propia reseña |
| DELETE | `/api/resenas/{id}/` | Borrar solo la propia reseña |

Filtros de reseñas:
- `/api/resenas/?juego=3` — reseñas del juego con ID 3.
- `/api/resenas/?mias=true` — reseñas del usuario autenticado.

## 3. Ejemplos de solicitudes

### Registro
`POST /api/auth/registro/`
```json
{
  "username": "jugador1",
  "email": "jugador@example.com",
  "password": "UnaClaveSegura-123",
  "password_confirmacion": "UnaClaveSegura-123"
}
```

### Login
`POST /api/auth/login/`
```json
{
  "username": "jugador1",
  "password": "UnaClaveSegura-123"
}
```
Respuesta aproximada:
```json
{
  "refresh": "...",
  "access": "..."
}
```

### Crear un juego (staff)
`POST /api/juegos/`
```json
{
  "titulo": "Ejemplo",
  "descripcion": "Descripción del videojuego",
  "plataforma": "PC",
  "anio_lanzamiento": 2024
}
```

### Crear reseña
`POST /api/resenas/`
```json
{
  "juego": 1,
  "contenido": "Me gustó el diseño y la jugabilidad.",
  "calificacion": 5
}
```
`calificacion` es opcional y admite valores del 1 al 5. El autor se obtiene del token, no del JSON enviado por Angular.

### Logout
`POST /api/auth/logout/`
```json
{
  "refresh": "..."
}
```

## 4. Consumir desde Angular

Guarda el access token tras el login y envíalo en las peticiones protegidas:

```typescript
const headers = new HttpHeaders({
  Authorization: `Bearer ${accessToken}`
});

this.http.get('http://127.0.0.1:8000/api/juegos/', { headers });
```

Recomendación: implementa un `HttpInterceptor` para adjuntar el token automáticamente y un servicio de autenticación para login/refresh/logout. No guardes credenciales en el código fuente.

## 5. Notas de seguridad

- `is_staff=True` habilita la gestión del catálogo por API. El superusuario creado con `createsuperuser` tiene ese permiso.
- Cada reseña queda asociada al usuario autenticado. Solo su autor puede modificarla o eliminarla.
- CORS está abierto para facilitar desarrollo local. En producción, limita `CORS_ALLOWED_ORIGINS` a los dominios reales.
- Cambia `SECRET_KEY`, desactiva `DEBUG` y configura `ALLOWED_HOSTS` antes de desplegar.
- La API usa JWT. Logout invalida el refresh token; el access token existente puede seguir vigente hasta que expire (30 minutos).
