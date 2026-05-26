# 🤖 Agente IA Inteligente — Monitor de Sistemas

```
Equipo "Equipo"
```

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Google-Gemini_Pro-orange?logo=google)](https://ai.google.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green?logo=mongodb)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Agente de inteligencia artificial de nivel premium para el monitoreo de infraestructura Linux, servidores web **Nginx**, bases de datos **MariaDB/MySQL**, uso de hardware (CPU, RAM, Disco) y microservicios en **Docker**. El agente detecta anomalías de forma autónoma con **Google Gemini**, ejecuta acciones correctivas de control, aprende patrones históricos en **PostgreSQL**, persiste conversaciones en **MongoDB** y protege sus recursos mediante autenticación **JWT con RBAC**.

---

## ✨ Características

| Característica | Descripción |
|---|---|
| 🔍 **Monitoreo en tiempo real** | Métricas de Nginx, MariaDB, CPU, RAM, Disco y contenedores Docker actualizadas cada 30s. |
| 🤖 **IA con Gemini Pro** | Análisis autónomo de anomalías, generación de diagnósticos y toma de decisiones inteligente. |
| 🔐 **Seguridad JWT y RBAC** | Autenticación robusta y control de acceso basado en roles (`admin`, `operator`, `viewer`) con permisos granulares. |
| 👥 **Gestión de Usuarios** | CRUD de usuarios y roles integrado con panel web administrativo. |
| 🐳 **Soporte Docker** | Estado de recursos, telemetría y visor de logs de contenedores en vivo, con soporte de encendido/apagado/reinicio. |
| ⚡ **Acciones correctivas** | Reiniciar Nginx, matar queries lentas, optimizar tablas MariaDB, limpiar logs de VPS y controlar Docker. |
| 🗄️ **Base de datos PostgreSQL** | Persistencia sólida de eventos de anomalías, historial de acciones, logs de auditoría y métricas. |
| 🍃 **Persistencia MongoDB** | Almacenamiento seguro e histórico del chat inteligente indexado por identificador de sesión. |
| 📊 **Dashboard Premium** | Interfaz oscura premium responsiva, con visualización de gráficas de hardware, visor de logs Docker terminal y chat en tiempo real. |

---

## 📋 Requisitos previos

- **Python** 3.9 o superior (probado en Python 3.11/3.12/3.14)
- **PostgreSQL** 14+ (persistencia del agente)
- **MongoDB** 5+ (opcional: historial de chat persistente; de lo contrario, se usa memoria local)
- **Acceso SSH** (clave privada o contraseña) a la VPS a monitorear
- **Google Gemini API Key** → [Obtener aquí](https://ai.google.dev/)

---

## 🚀 Instalación y Despliegue

### 1. Clonar el proyecto
```bash
cd agente-ia-inteligente
```

### 2. Crear y activar el entorno virtual
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar plantilla
cp .env.example .env
```
Edita `.env` con tus valores de base de datos PostgreSQL, MongoDB, API de Gemini, contraseñas y llaves de acceso SSH a la VPS.

### 5. Sembrar (Seed) el administrador inicial
Crea el usuario administrador inicial para poder iniciar sesión en el dashboard:
```bash
python seed_admin.py
```
*(Toma los valores `ADMIN_EMAIL`, `ADMIN_USERNAME` y `ADMIN_PASSWORD` definidos en tu archivo `.env`)*

### 6. Levantar el Servidor
```bash
python app.py
```
Abre tu navegador en: **http://localhost:5000** e ingresa con tus credenciales de administrador.

---

## 📁 Estructura del Proyecto

```
agente-ia-inteligente/
├── app.py                  # API REST Flask 3.0 (punto de entrada)
├── agente.py               # Lógica del Agente Inteligente (Gemini)
├── auth.py                 # Seguridad JWT y Control de Accesos (RBAC)
├── config.py               # Configuración central (carga de .env)
├── seed_admin.py           # Inyección inicial del usuario administrador
├── build_linux.sh          # Compilador multi-arquitectura para producción Linux
├── requirements.txt        # Dependencias Python
├── .env.example            # Plantilla de variables de entorno
│
├── adaptadores/
│   ├── __init__.py         # Exportación de adaptadores
│   ├── docker.py           # Telemetría y control de Docker (SSH)
│   ├── sistema.py          # Métricas de hardware local/remoto (SSH/psutil)
│   ├── nginx.py            # Estado y logs de Nginx (SSH)
│   ├── mariadb.py          # Estadísticas y consultas MariaDB (PyMySQL)
│   ├── postgres.py         # Conectividad PostgreSQL (psycopg2)
│   └── mongodb.py          # Conectividad MongoDB (pymongo)
│
├── templates/
│   ├── index.html          # Dashboard principal
│   ├── login.html          # Interfaz de inicio de sesión
│   └── admin_usuarios.html # Panel administrativo de usuarios y roles
│
└── static/
    ├── css/style.css       # Estilos visuales del dashboard
    └── js/script.js        # Lógica de fetching, chat e interacción
```

---

## 🌐 Endpoints de la API (Protegidos mediante JWT)

### Autenticación y Usuarios
| Método | Ruta | Permiso Requerido | Descripción |
|---|---|---|---|
| `POST` | `/api/auth/login` | *Ninguno* | Autentica credenciales y emite el token JWT |
| `GET` | `/api/auth/me` | Autenticado | Retorna los detalles y permisos del usuario activo |
| `POST` | `/api/auth/cambiar-password` | Autenticado | Modifica la contraseña del usuario |
| `GET` | `/api/auth/roles` | Autenticado | Lista los roles y permisos del sistema |
| `GET` | `/api/usuarios` | `manage_users` | Lista todos los usuarios (solo Admin) |
| `POST` | `/api/usuarios` | `manage_users` | Crea un nuevo usuario y su UUID v5 determinístico |
| `PUT` | `/api/usuarios/<id>` | `manage_users` | Modifica rol, nombre o estado de un usuario |
| `DELETE` | `/api/usuarios/<id>` | `manage_users` | Elimina permanentemente a un usuario |

### Métricas y Logs (Lectura)
| Método | Ruta | Permiso Requerido | Descripción |
|---|---|---|---|
| `GET` | `/api/health` | *Ninguno* | Estado de salud y conectividad de componentes |
| `GET` | `/api/metricas/nginx` | `read_metrics` | Obtiene métricas actuales de Nginx |
| `GET` | `/api/metricas/mariadb` | `read_metrics` | Obtiene métricas y procesos de MariaDB |
| `GET` | `/api/metricas/sistema` | `read_metrics` | Obtiene porcentaje de CPU, RAM y uso de Disco |
| `GET` | `/api/metricas/docker` | `read_metrics` | Obtiene estatus y recursos de contenedores Docker |
| `GET` | `/api/docker/logs` | `read_metrics` | Lee logs detallados de un contenedor específico |

### Inteligencia Artificial e Historial
| Método | Ruta | Permiso Requerido | Descripción |
|---|---|---|---|
| `POST` | `/api/analizar` | `analyze_anomalies` | Gemini analiza las métricas consolidadas |
| `POST` | `/api/preguntas` | `use_ai_chat` | Envía una consulta técnica al chat inteligente |
| `GET` | `/api/eventos` | `read_events` | Obtiene anomalías y eventos registrados en BD |
| `GET` | `/api/acciones` | `read_actions` | Obtiene logs de acciones correctivas |

### Control de Servicios y VPS
| Método | Ruta | Permiso Requerido | Cuerpo JSON (Ejemplo) | Descripción |
|---|---|---|---|---|
| `POST` | `/api/ejecutar-accion` | `execute_actions` | `{"accion": "reiniciar_nginx"}` | Reinicia Nginx via SSH |
| `POST` | `/api/ejecutar-accion` | `execute_actions` | `{"accion": "optimizar_bd", "parametros": {"base_datos": "mydb"}}` | Ejecuta OPTIMIZE TABLE |
| `POST` | `/api/ejecutar-accion` | `execute_actions` | `{"accion": "matar_query", "parametros": {"proceso_id": 42}}` | Termina una query lenta |
| `POST` | `/api/ejecutar-accion` | `execute_actions` | `{"accion": "limpiar_logs"}` | Limpia logs de VPS |
| `POST` | `/api/ejecutar-accion` | `execute_actions` | `{"accion": "iniciar_contenedor", "parametros": {"contenedor_id": "web"}}` | Enciende un contenedor |
| `POST` | `/api/ejecutar-accion` | `execute_actions` | `{"accion": "detener_contenedor", "parametros": {"contenedor_id": "web"}}` | Detiene un contenedor |
| `POST` | `/api/ejecutar-accion` | `execute_actions` | `{"accion": "reiniciar_contenedor", "parametros": {"contenedor_id": "web"}}` | Reinicia un contenedor |

---

## 🛠️ Compilación para Producción (Linux Executables)

El proyecto incluye el script optimizado `build_linux.sh` para empaquetar toda la aplicación (Flask, dependencias, static y templates) en binarios ejecutables e independientes para Linux AMD64 (x86_64) y ARM64 (aarch64/Graviton/Raspberry Pi) usando Docker:

```bash
# Conceder permisos de ejecución
chmod +x build_linux.sh

# Compilar
./build_linux.sh
```

El resultado compilado y listo para desplegar se generará automáticamente en la carpeta `dist/deploy/`, la cual contiene el binario compilado correspondiente, la plantilla de configuración `.env` y las carpetas `templates`, `static` y `keys`.

---

## ❗ Solución de Problemas (Troubleshooting)

### Error: `Cannot find module jwt`
→ No tienes la dependencia instalada en tu entorno activo de Python. Asegúrate de activar tu entorno virtual (`venv`) y ejecutar: `pip install -r requirements.txt`.

---

## 🗺️ Roadmap Completado

- `[x]` Autenticación JWT y control de accesos por roles y permisos (RBAC).
- `[x]` Monitoreo detallado del Sistema (CPU, RAM, Disco Duro) via SSH o local.
- `[x]` Monitoreo, lectura de logs y control de contenedores Docker en vivo.
- `[x]` Persistencia avanzada e historial de chats en MongoDB.
- `[x]` Compilador multiplataforma multi-arquitectura nativo.
- `[ ]` Alertas automáticas en tiempo real via Slack o Telegram.

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Libre de uso y modificación.

---

> **Agente IA Inteligente** — Diseñado e implementado con arquitectura premium para administración avanzada de servidores e inteligencia de monitoreo.
