#!/bin/bash
# Script para diagnosticar y resolver bloqueos B1 y B3
# B1: Dependencias testing no instaladas (pytest)
# B3: Dependencias qwen-poc no instaladas (requests)

echo "🚀 SETUP TESTING ENVIRONMENT - RESOLVIENDO BLOQUEOS B1 y B3"
echo "=========================================================="

# Configuración
PROJECT_DIR="/home/luis/code/AIReels"
QWEN_POC_DIR="$PROJECT_DIR/qwen-poc"
INSTAGRAM_UPLOAD_DIR="$PROJECT_DIR/instagram-upload"

echo "📋 Diagnóstico inicial..."
echo ""

# 1. Verificar Python disponible
echo "1. Verificando Python..."
python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python 3 disponible"
else
    echo "❌ Python 3 no disponible"
    exit 1
fi

# 2. Verificar pip disponible
echo "2. Verificando pip..."
python3 -m pip --version
if [ $? -eq 0 ]; then
    echo "✅ pip disponible"
else
    echo "❌ pip no disponible"
    exit 1
fi

# 3. Verificar entorno virtual
echo "3. Verificando entorno virtual..."
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "✅ Entorno virtual 'venv' existe"

    # Intentar activar
    if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
        echo "✅ Script activate existe"
    else
        echo "⚠️ Script activate no encontrado"
    fi
else
    echo "⚠️ Entorno virtual 'venv' no existe"
fi

# 4. Diagnosticar B1: Dependencias testing
echo "4. Diagnosticando B1 (dependencias testing)..."
python3 -c "import pytest" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ pytest instalado"
else
    echo "❌ pytest NO instalado (B1 ACTIVO)"
fi

python3 -c "import pytest_asyncio" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ pytest-asyncio instalado"
else
    echo "❌ pytest-asyncio NO instalado (B1 ACTIVO)"
fi

# 5. Diagnosticar B3: Dependencias qwen-poc
echo "5. Diagnosticando B3 (dependencias qwen-poc)..."
python3 -c "import requests" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ requests instalado"
else
    echo "❌ requests NO instalado (B3 ACTIVO)"
fi

python3 -c "import dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ python-dotenv instalado"
else
    echo "❌ python-dotenv NO instalado (B3 ACTIVO)"
fi

echo ""
echo "=========================================================="
echo "📊 RESULTADO DEL DIAGNÓSTICO:"

# Contar problemas
B1_PROBLEMS=0
B3_PROBLEMS=0

if ! python3 -c "import pytest" 2>/dev/null; then B1_PROBLEMS=$((B1_PROBLEMS+1)); fi
if ! python3 -c "import pytest_asyncio" 2>/dev/null; then B1_PROBLEMS=$((B1_PROBLEMS+1)); fi
if ! python3 -c "import requests" 2>/dev/null; then B3_PROBLEMS=$((B3_PROBLEMS+1)); fi
if ! python3 -c "import dotenv" 2>/dev/null; then B3_PROBLEMS=$((B3_PROBLEMS+1)); fi

echo "  B1 (testing): $B1_PROBLEMS problemas"
echo "  B3 (qwen-poc): $B3_PROBLEMS problemas"
echo "  Total: $((B1_PROBLEMS + B3_PROBLEMS)) problemas"

echo ""
echo "=========================================================="
echo "🛠️ SOLUCIONES PROPUESTAS (ejecutar una):"

# Opción 1: Instalar en user site (más permisos)
echo "1. INSTALAR EN USER SITE (más permisos):"
echo "   python3 -m pip install --user pytest pytest-asyncio pytest-playwright pytest-cov pytest-mock"
echo "   python3 -m pip install --user requests python-dotenv"

# Opción 2: Instalar globalmente (si hay permisos)
echo "2. INSTALAR GLOBALMENTE (si hay permisos):"
echo "   pip3 install pytest pytest-asyncio pytest-playwright pytest-cov pytest-mock"
echo "   pip3 install requests python-dotenv"

# Opción 3: Configurar entorno virtual
echo "3. CONFIGURAR ENTORNO VIRTUAL:"
echo "   cd $PROJECT_DIR"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install pytest pytest-asyncio pytest-playwright pytest-cov pytest-mock"
echo "   pip install requests python-dotenv"

# Opción 4: Instalar solo lo necesario para pruebas E2E
echo "4. INSTALAR MINIMO PARA PRUEBAS E2E:"
echo "   python3 -m pip install --user pytest requests"

echo ""
echo "=========================================================="
echo "🎯 RECOMENDACIÓN PARA Taylor QA Engineer:"

if [ $B1_PROBLEMS -gt 0 ] || [ $B3_PROBLEMS -gt 0 ]; then
    echo "⚠️ BLOQUEOS ACTIVOS - PRUEBAS E2E IMPOSIBLES"
    echo ""
    echo "Sugiero ejecutar Opción 1 primero:"
    echo ""
    echo "Ejecutar estos comandos:"
    echo "python3 -m pip install --user pytest pytest-asyncio"
    echo "python3 -m pip install --user requests python-dotenv"
    echo ""
    echo "Después verificar:"
    echo "python3 -c \"import pytest; import requests; print('✅ Dependencias instaladas')\""
else
    echo "✅ NO hay bloqueos - pruebas E2E posibles"
    echo ""
    echo "Verificar que qwen-poc puede ejecutar:"
    echo "cd $QWEN_POC_DIR && python3 pipeline.py --help"
fi

echo ""
echo "=========================================================="
echo "📝 PARA REGISTRAR EN TEAM_TASK_UPDATES.md:"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
echo ""
echo "## $TIMESTAMP - Taylor QA Engineer - B1_B3_RESOLUTION"
echo "**Estado:** IN_PROGRESS"
echo "**Cambio:** Diagnosticando y resolviendo bloqueos B1 y B3"
echo "**Detalles:**"
echo "- Diagnosticados $B1_PROBLEMS problemas B1 (testing)"
echo "- Diagnosticados $B3_PROBLEMS problemas B3 (qwen-poc)"
echo "- Total: $((B1_PROBLEMS + B3_PROBLEMS)) problemas"
echo "- Ejecutado script de diagnóstico"
echo "- Opciones de solución documentadas"
echo "**Siguiente:** Ejecutar Opción 1 (install --user)"
echo "**Blocker:** Permisos de instalación de paquetes"
echo "**Evidencia:** Diagnóstico completo, script ejecutado"

echo ""
echo "=========================================================="
echo "🚀 EJECUTAR AHORA PARA RESOLVER (Taylor):"

echo "# Prueba instalación mínima primero"
echo "python3 -m pip install --user pytest requests"

echo ""
echo "Si funciona, continuar con:"
echo "python3 -m pip install --user pytest-asyncio pytest-playwright pytest-cov pytest-mock"
echo "python3 -m pip install --user python-dotenv"