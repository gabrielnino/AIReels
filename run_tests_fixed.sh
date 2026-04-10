#!/bin/bash
# Test runner fijo que usa sistema Python en lugar de venv

set -e  # Exit on error

echo "🚀 EJECUTANDO TESTS CON ENTORNO CORREGIDO"
echo "=========================================="

# Usar sistema Python para evitar issues de venv
PYTHON="/usr/bin/python3"
PROJECT_ROOT="/home/luis/code/AIReels"

echo "🐍 Python: $PYTHON"
echo "📁 Project: $PROJECT_ROOT"
echo "🕐 Time: $(date '+%H:%M:%S')"

# Configurar environment para tests
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/instagram-upload:$PROJECT_ROOT/qwen-poc"

# Cargar variables de entorno de test si existe
if [ -f "$PROJECT_ROOT/.env.test" ]; then
    echo "✅ Cargando .env.test"
    # Simple load of env vars (para bash)
    set -a
    source "$PROJECT_ROOT/.env.test"
    set +a
fi

# Función para ejecutar tests
run_pytest() {
    local test_target="$1"
    local extra_args="$2"

    echo ""
    echo "🔧 Ejecutando: $test_target"
    echo "========================================"

    cd "$PROJECT_ROOT"

    $PYTHON -m pytest "$test_target" \
        -v \
        --tb=short \
        --disable-warnings \
        --cov-context=test \
        $extra_args

    return $?
}

# Manejar argumentos
if [ $# -eq 0 ]; then
    # Sin argumentos: run all critical tests
    echo "📋 Ejecutando tests críticos..."

    # Tests de instagram-upload primero
    run_pytest "instagram-upload/tests/unit/auth/test_browser_service.py" "-x"
    run_pytest "instagram-upload/tests/unit/auth/test_login_manager.py" "-x"
    run_pytest "instagram-upload/tests/unit/upload/test_video_uploader.py" "-x"

    echo ""
    echo "✅ Ejecución completa de tests críticos"

else
    # Con argumentos
    case "$1" in
        instagram)
            echo "📱 Ejecutando tests de instagram-upload"
            run_pytest "instagram-upload/tests/" "$2"
            ;;
        qwen)
            echo "🤖 Ejecutando tests de qwen-poc"
            run_pytest "qwen-poc/tests/" "$2"
            ;;
        integration)
            echo "🔗 Ejecutando tests de integration"
            run_pytest "tests/" "$2"
            ;;
        all)
            echo "🌐 Ejecutando todos los tests"
            run_pytest "." "$2"
            ;;
        file)
            if [ -n "$2" ]; then
                run_pytest "$2" "$3"
            else
                echo "❌ Error: Necesita especificar archivo para 'file'"
                exit 1
            fi
            ;;
        *)
            # Asumir que es un path directo
            run_pytest "$1" "$2"
            ;;
    esac
fi

echo ""
echo "=========================================="
echo "🏁 TESTS COMPLETADOS"
echo "⏰ Time: $(date '+%H:%M:%S')"