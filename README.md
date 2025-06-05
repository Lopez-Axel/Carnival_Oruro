# Carnaval de Oruro 2025 - Sistema de Venta de Entradas

<!-- 
Para descargar este archivo:
1. Copia todo el contenido de este README
2. Créa un nuevo archivo llamado "README.md" en la raíz de tu proyecto
3. Pega el contenido
4. ¡Listo!
-->

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Astro](https://img.shields.io/badge/Astro-FF5D01?style=for-the-badge&logo=astro&logoColor=white)](https://astro.build/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)

> Plataforma integral para la venta de entradas y gestión del Carnaval de Oruro 2025, el patrimonio cultural inmaterial de la humanidad.

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🛠️ Tecnologías](#️-tecnologías)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [⚙️ Instalación](#️-instalación)
- [🚀 Uso](#-uso)
- [📚 API Endpoints](#-api-endpoints)
- [👥 Roles de Usuario](#-roles-de-usuario)
- [🗃️ Base de Datos](#️-base-de-datos)
- [🎨 Diseño](#-diseño)
- [🤝 Contribuir](#-contribuir)
- [📄 Licencia](#-licencia)

## ✨ Características

### 🎫 Para Clientes
- **Compra de entradas** con selección de asientos interactiva
- **Códigos QR** para validación en el evento
- **Gestión de boletos** con descarga PDF
- **Mapa de ubicación** de vendedores y servicios
- **Sistema de pagos** seguro y múltiples métodos

### 💼 Para Vendedores
- **Panel de control** con estadísticas de ventas
- **Gestión de inventario** de asientos
- **Sistema de comisiones** automático
- **Reportes** de ventas detallados
- **Perfil público** con calificaciones

### 🔧 Para Administradores
- **Panel administrativo** completo
- **Gestión de eventos** y programación
- **Control de vendedores** y solicitudes
- **Mapa interactivo** con servicios del carnaval
- **Sistema de noticias** y comunicados
- **Gestión de bandas** y artistas
- **Estadísticas** y reportes avanzados

### 🗺️ Características Especiales
- **Mapa interactivo** con servicios (baños, comida, estacionamiento)
- **Ruta oficial del carnaval** cargada desde GeoJSON
- **Sistema de notificaciones** en tiempo real
- **Diseño responsivo** optimizado para móviles
- **Tema personalizado** inspirado en el Carnaval de Oruro

## 🛠️ Tecnologías

### Frontend
- **[Astro](https://astro.build/)** - Framework web moderno
- **CSS Variables** - Sistema de diseño personalizado
- **JavaScript Vanilla** - Interactividad sin frameworks pesados
- **Leaflet** - Mapas interactivos
- **Lucide Icons** - Iconografía moderna

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - API REST de alto rendimiento
- **Python 3.8+** - Lenguaje de programación
- **Pydantic** - Validación de datos
- **AsyncPG** - Driver PostgreSQL asíncrono
- **Jose** - Manejo de JWT tokens

### Base de Datos y Servicios
- **[PostgreSQL](https://postgresql.org/)** - Base de datos principal
- **[Supabase](https://supabase.com/)** - Backend as a Service
  - Autenticación
  - Storage de archivos
  - Base de datos
- **[SendGrid](https://sendgrid.com/)** - Servicio de emails

## 📁 Estructura del Proyecto

```
carnaval-oruro-2025/
├── 📂 src/
│   ├── 📂 components/          # Componentes reutilizables
│   │   ├── Card.astro
│   │   ├── Modal.astro
│   │   ├── Button.astro
│   │   └── ModalRegistro.astro
│   ├── 📂 layouts/             # Layouts de página
│   │   └── MainLayout.astro
│   ├── 📂 pages/              # Páginas del sitio
│   │   ├── 📂 Cliente/        # Páginas de clientes
│   │   ├── 📂 Vendedor/       # Páginas de vendedores
│   │   └── 📂 Administrador/  # Páginas de admin
│   └── 📂 styles/
│       └── global.css         # Estilos globales
├── 📂 app/                    # Backend FastAPI
│   ├── 📂 routes/             # Rutas de la API
│   │   ├── admin.py
│   │   └── vendor.py
│   ├── 📂 schemas/            # Modelos Pydantic
│   │   └── admin.py
│   ├── 📂 services/           # Lógica de negocio
│   │   ├── admin_service.py
│   │   ├── storage_service.py
│   │   └── email_service.py
│   ├── database.py            # Configuración DB
│   ├── dependencies.py        # Dependencias
│   └── main.py               # Aplicación principal
├── 📂 public/
│   ├── 📂 images/            # Imágenes estáticas
│   └── ruta_carnaval.geojson # Ruta oficial del carnaval
├── package.json
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Instalación

### 📋 Prerrequisitos

- **Node.js** 18+ y npm
- **Python** 3.8+
- **PostgreSQL** 13+
- Cuenta en **Supabase**
- Cuenta en **SendGrid** (opcional)

### 🔧 Configuración

1. **Clona el repositorio**
```bash
git clone https://github.com/tu-usuario/carnaval-oruro-2025.git
cd carnaval-oruro-2025
```

2. **Instala dependencias del frontend**
```bash
npm install
```

3. **Instala dependencias del backend**
```bash
pip install -r requirements.txt
```

4. **Configura variables de entorno**
```bash
cp .env.example .env
```

Edita el archivo `.env`:
```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/carnaval_oruro

# Supabase
SUPABASE_URL=tu_supabase_url
SUPABASE_ANON_KEY=tu_supabase_anon_key
SUPABASE_SERVICE_KEY=tu_supabase_service_key
SUPABASE_JWT_SECRET=tu_jwt_secret

# SendGrid (opcional)
SENDGRID_API_KEY=tu_sendgrid_api_key

# Configuración
JWT_ALGORITHM=HS256
ENVIRONMENT=development
```

5. **Configura la base de datos**
```sql
-- Crear las tablas principales
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    role VARCHAR DEFAULT 'cliente',
    phone TEXT,
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT false,
    verification_status VARCHAR DEFAULT 'pending',
    last_login TIMESTAMPTZ
);

-- Ver el archivo SQL completo en la documentación
```

## 🚀 Uso

### 🎬 Desarrollo

**Frontend (Astro)**
```bash
npm run dev
# Abre http://localhost:4321
```

**Backend (FastAPI)**
```bash
uvicorn app.main:app --reload --port 8000
# API disponible en http://localhost:8000
# Documentación en http://localhost:8000/docs
```

### 🏗️ Producción

**Frontend**
```bash
npm run build
npm run preview
```

**Backend**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Endpoints

### 🔐 Autenticación
```http
POST   /api/auth/signin           # Iniciar sesión
POST   /api/auth/signup           # Registrarse
POST   /api/auth/signout          # Cerrar sesión
GET    /api/auth/user             # Usuario actual
```

### 👥 Administración
```http
GET    /api/admin/health          # Estado del sistema
GET    /api/admin/stats           # Estadísticas generales

# Eventos
GET    /api/admin/events          # Listar eventos
POST   /api/admin/events          # Crear evento
GET    /api/admin/events/:id      # Obtener evento
PUT    /api/admin/events/:id      # Actualizar evento
DELETE /api/admin/events/:id      # Eliminar evento

# Servicios del mapa
GET    /api/admin/map-services    # Servicios en mapa
POST   /api/admin/map-services    # Crear servicio
PUT    /api/admin/map-services/:id # Actualizar servicio
DELETE /api/admin/map-services/:id # Eliminar servicio

# Bandas
GET    /api/admin/bands           # Listar bandas
POST   /api/admin/bands           # Crear banda
GET    /api/admin/bands/:id       # Obtener banda

# Noticias
GET    /api/admin/news            # Listar noticias
POST   /api/admin/news            # Crear noticia
PUT    /api/admin/news/:id        # Actualizar noticia
```

### 🛒 Vendedores
```http
GET    /api/vendor/applications   # Solicitudes de vendedor
POST   /api/vendor/apply          # Solicitar ser vendedor
GET    /api/vendor/status         # Estado de solicitud
```

### 🧪 Testing
```http
GET    /api/test-all-services     # Probar todos los servicios
GET    /api/test-storage-config   # Probar configuración storage
GET    /api/test-email-config     # Probar configuración email
```

## 👥 Roles de Usuario

### 🛒 Cliente
- Comprar entradas
- Ver eventos disponibles
- Gestionar boletos comprados
- Solicitar ser vendedor

### 💼 Vendedor
- Vender entradas con comisión
- Gestionar inventario de asientos
- Ver estadísticas de ventas
- Perfil público con calificaciones

### 🔧 Administrador
- Control total del sistema
- Gestión de eventos y contenido
- Aprobar/rechazar vendedores
- Configurar servicios del mapa
- Acceso a estadísticas completas

## 🗃️ Base de Datos

### 📊 Tablas Principales

- **`user_profiles`** - Perfiles de usuario
- **`events`** - Eventos del carnaval
- **`event_activities`** - Actividades de eventos
- **`bands`** - Bandas y artistas
- **`map_services`** - Servicios en el mapa
- **`carnival_zones`** - Zonas del carnaval
- **`news`** - Noticias y comunicados
- **`activity_log`** - Log de actividades

### 🔄 Relaciones
- Los eventos pueden tener múltiples actividades
- Los servicios están geolocalizados en el mapa
- Los usuarios tienen roles específicos
- Sistema de log para auditoría

## 🎨 Diseño

### 🎨 Sistema de Colores
```css
:root {
  --primary: #1a237e;        /* Azul marino profundo */
  --secondary: #d32f2f;      /* Rojo carnaval */
  --accent: #ff6b35;         /* Naranja vibrante */
  --success: #2e7d32;        /* Verde esmeralda */
  --warning: #f57c00;        /* Dorado */
}
```

### 📱 Responsive Design
- **Móvil primero** con breakpoints adaptativos
- **Grids CSS** flexibles para layouts
- **Componentes reutilizables** con Astro
- **Animaciones CSS** suaves y accesibles

### 🎭 Tema Carnaval
- Inspirado en los colores tradicionales del Carnaval de Oruro
- Efectos glassmorphism para elementos flotantes
- Gradientes que evocan la festividad
- Iconografía relacionada con la cultura boliviana

## 🤝 Contribuir

¡Contribuciones son bienvenidas! Por favor:

1. **Fork** el repositorio
2. Crea una **rama** para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. **Commit** tus cambios (`git commit -m 'Agrega nueva característica'`)
4. **Push** a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un **Pull Request**

### 📝 Estándares de Código

- **ESLint** para JavaScript
- **Black** para Python
- **Prettier** para formateo
- **Conventional Commits** para mensajes

### 🧪 Testing

```bash
# Frontend
npm run test

# Backend
pytest

# E2E
npm run test:e2e
```

## 📞 Soporte

- **Email**: soporte.carnaval.oruro@gmail.com
- **Teléfono**: +591 999 888 777
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/carnaval-oruro-2025/issues)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">
  <h3>🎭 Desarrollado con ❤️ para el Carnaval de Oruro 2025</h3>
  <p><em>"Obra Maestra del Patrimonio Oral e Intangible de la Humanidad"</em></p>
  
  [![Made in Bolivia](https://img.shields.io/badge/Made%20in-Bolivia-red?style=for-the-badge)](https://bolivia.travel/)
  [![UNESCO](https://img.shields.io/badge/UNESCO-World%20Heritage-blue?style=for-the-badge)](https://whc.unesco.org/)
</div>

## 🙏 Agradecimientos

- **UNESCO** por reconocer el Carnaval de Oruro como Patrimonio de la Humanidad
- **Gobierno Municipal de Oruro** por el apoyo institucional
- **Fraternidades folklóricas** que mantienen viva la tradición
- **Comunidad de desarrolladores** que contribuyeron al proyecto

---

⭐ **¡Dale una estrella si este proyecto te fue útil!** ⭐
