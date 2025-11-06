# Sistema de Reclutamiento con IA - Backend

Backend desarrollado con Django REST Framework para un sistema de reclutamiento inteligente con funcionalidades de matching de candidatos usando inteligencia artificial.

## 🚀 Tecnologías

- **Django 5.2.7** - Framework web
- **Django REST Framework 3.16.1** - API REST
- **MySQL** - Base de datos
- **JWT** - Autenticación
- **Python 3.11+**

## 📋 Prerequisitos

- Python 3.11 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/DDCT2003/Proyecto-Capstone-BackEnd-.git
cd Proyecto-Capstone-BackEnd-
```

### 2. Crear y activar entorno virtual

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y actualiza los valores:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales:

```env
SECRET_KEY=genera-una-clave-secreta-unica
DEBUG=True
DB_PASSWORD=tu_contraseña_mysql
```

**Importante:** Si no usas variables de entorno, debes editar manualmente `core/settings.py` con tu configuración de MySQL.

### 5. Configurar MySQL

Asegúrate de que MySQL esté corriendo y crea la base de datos:

```sql
CREATE DATABASE recruitment_ai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### 8. Iniciar el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## 📁 Estructura del Proyecto

```
Proyecto-Capstone-BackEnd-/
├── accounts/           # Autenticación y gestión de usuarios
├── projects/           # Gestión de proyectos
├── recruiting/         # Sistema de reclutamiento y aplicaciones
├── core/              # Configuración principal de Django
├── media/             # Archivos subidos (CVs)
├── manage.py          # Script de Django
└── requirements.txt   # Dependencias del proyecto
```

## 🔌 Endpoints principales

### Autenticación

- `POST /api/accounts/register/` - Registrar nuevo usuario
- `POST /api/auth/jwt/create/` - Login (obtener tokens)
- `POST /api/auth/jwt/refresh/` - Renovar token de acceso
- `POST /api/auth/jwt/verify/` - Verificar token
- `GET /api/accounts/me/` - Obtener perfil del usuario autenticado

### Proyectos

- `GET /api/projects/` - Listar proyectos
- `POST /api/projects/` - Crear proyecto (requiere autenticación)
- `GET /api/projects/{id}/` - Ver detalle de proyecto
- `PUT/PATCH /api/projects/{id}/` - Actualizar proyecto
- `DELETE /api/projects/{id}/` - Eliminar proyecto

### Aplicaciones

- `GET /api/recruiting/applications/` - Listar aplicaciones del usuario
- `POST /api/recruiting/applications/` - Aplicar a un proyecto
- `GET /api/recruiting/applications/{id}/` - Ver detalle de aplicación

## 🔐 Validaciones Implementadas

### Registro de Usuario

- ✅ Email único y con formato válido
- ✅ Username único
- ✅ Contraseña segura:
  - Mínimo 8 caracteres
  - Al menos una letra mayúscula
  - Al menos una letra minúscula
  - Al menos un número
  - Al menos un carácter especial (!@#$%^&\*(),.?":{}|<>)
  - No debe contener el nombre de usuario

## 🧪 Ejecutar Tests

```bash
# Test de funcionalidades de candidato
python test_candidate_features.py

# Test de validaciones de contraseña
python test_password_validations.py
```

## 🌐 CORS

El backend está configurado para aceptar peticiones desde:

- `http://localhost:5173` (Vite - React)
- `http://localhost:5174` (Puerto alternativo de Vite)

Si tu frontend usa un puerto diferente, actualiza `CORS_ALLOWED_ORIGINS` en `settings.py`.

## 🐛 Troubleshooting

### Error: "Access denied for user 'root'@'localhost'"

- Verifica que MySQL esté corriendo
- Verifica las credenciales en `settings.py` o en tu archivo `.env`
- Asegúrate de que la base de datos `recruitment_ai_db` exista

### Error: "No module named 'MySQLdb'"

```bash
pip install mysqlclient
```

### Error de CORS

- Verifica que el puerto del frontend esté en `CORS_ALLOWED_ORIGINS`
- Asegúrate de que el servidor Django esté corriendo

## 📝 Notas Importantes

1. **NO subir a GitHub:**

   - Archivo `.env` con credenciales
   - Carpeta `media/` con CVs de usuarios
   - Base de datos SQLite (`db.sqlite3`) si existe

2. **Seguridad:**

   - Cambia `SECRET_KEY` en producción
   - Usa contraseñas fuertes para MySQL
   - Configura `DEBUG=False` en producción
   - Actualiza `ALLOWED_HOSTS` en producción

3. **Base de datos:**
   - El proyecto usa MySQL
   - Si compartes la base de datos, exporta/importa con `mysqldump`

## 👥 Contribuidores

- Juan Alvarez

## 📄 Licencia

Este proyecto es parte de un proyecto de titulación.
