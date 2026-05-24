#!/bin/bash
# ==============================================================================
# build_linux.sh - Compilador multi-arquitectura para Linux (AMD64 y ARM64)
# REQUIERE DOCKER ACTIVO
# ==============================================================================
set -e

echo "🤖 Iniciando compilación multi-arquitectura del Agente IA..."

# 1. Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado en este sistema."
    echo "Este script requiere Docker para realizar la compilación cruzada."
    exit 1
fi

# 2. Verificar si el servicio de Docker está en ejecución
if ! docker ps &> /dev/null; then
    echo "❌ Error: El servicio de Docker no está activo o no tienes permisos (sudo)."
    echo "Asegúrate de iniciar el servicio de Docker o ejecutar: sudo ./build_linux.sh"
    exit 1
fi

echo "🐳 Docker detectado y activo. Se generarán binarios para AMD64 y ARM64..."

# 3. Configurar soporte de emulación QEMU en Docker
echo "🔧 Verificando y habilitando soporte QEMU binfmt en Docker..."
docker run --privileged --rm tonistiigi/binfmt --install all &> /dev/null || true

# 4. Compilar versión AMD64 (x86_64)
echo "⚡ Compilando ejecutable para Linux AMD64 (x86_64) vía Docker..."
docker run --rm --platform linux/amd64 -v "$(pwd):/app" python:3.11-slim bash -c \
    "apt-get update && apt-get install -y binutils gcc python3-dev && pip install --upgrade pip && cd /app && pip install -r requirements.txt && pip install pyinstaller && pyinstaller --onefile --name='agente-ia-linux-amd64' --clean app.py"

# 5. Compilar versión ARM64 (aarch64)
echo "⚡ Compilando ejecutable para Linux ARM64 (aarch64) vía Docker..."
docker run --rm --platform linux/arm64 -v "$(pwd):/app" python:3.11-slim bash -c \
    "apt-get update && apt-get install -y binutils gcc python3-dev && pip install --upgrade pip && cd /app && pip install -r requirements.txt && pip install pyinstaller && pyinstaller --onefile --name='agente-ia-linux-arm64' --clean app.py"

# Restaurar propiedad de los archivos creados por Docker (root) al usuario host
echo "🔑 Ajustando propiedad de los archivos compilados para el usuario host..."
docker run --rm -v "$(pwd):/app" python:3.11-slim chown -R $(id -u):$(id -g) /app/dist /app/build 2>/dev/null || true

# 6. Crear estructura de distribución para despliegue
echo "📁 Estructurando carpeta de distribución 'dist/deploy'..."
DEPLOY_DIR="dist/deploy"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR/keys"

# Copiar ambos binarios generados a la carpeta de despliegue
cp "dist/agente-ia-linux-amd64" "$DEPLOY_DIR/"
cp "dist/agente-ia-linux-arm64" "$DEPLOY_DIR/"

# Copiar carpetas web y plantilla de configuración
cp -r templates "$DEPLOY_DIR/"
cp -r static "$DEPLOY_DIR/"
cp .env.example "$DEPLOY_DIR/.env"
touch "$DEPLOY_DIR/keys/.gitkeep"

echo "------------------------------------------------------------"
echo "🎉 ¡Compilación multi-arquitectura completada exitosamente!"
echo "------------------------------------------------------------"
echo "La carpeta lista para despliegue se encuentra en:"
echo "👉 $(pwd)/dist/deploy"
echo ""
echo "Binarios empaquetados:"
echo "✅ dist/deploy/agente-ia-linux-amd64  (Servidores comunes Intel/AMD x86_64)"
echo "✅ dist/deploy/agente-ia-linux-arm64  (Servidores ARM, ej: Raspberry Pi, AWS Graviton)"
echo ""
echo "Para desplegar en producción:"
echo "1. Copia la carpeta 'deploy' a tu servidor."
echo "2. Edita el archivo '.env' con tus credenciales reales."
echo "3. Otorga permisos de ejecución al binario correspondiente a tu servidor:"
echo "   chmod +x agente-ia-linux-amd64  # o agente-ia-linux-arm64"
echo "4. Inicia el servidor:"
echo "   ./agente-ia-linux-amd64         # o ./agente-ia-linux-arm64"
echo "------------------------------------------------------------"
