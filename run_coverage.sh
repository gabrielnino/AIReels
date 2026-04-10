#!/bin/bash
# Script para generar reporte de cobertura

echo "📊 GENERANDO REPORTE DE COBERTURA ACTUALIZADO"
echo "=============================================="

PYTHON="/usr/bin/python3"
PROJECT_ROOT="/home/luis/code/AIReels"

cd "$PROJECT_ROOT"

export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/instagram-upload:$PROJECT_ROOT/qwen-poc"

# Cargar .env.test si existe
if [ -f ".env.test" ]; then
    echo "✅ Cargando .env.test"
    set -a
    source ".env.test"
    set +a
fi

echo "🔧 Ejecutando coverage report..."
echo ""

$PYTHON -m pytest instagram-upload/tests/ \
    --cov=instagram-upload/src \
    --cov-report=term-missing \
    --cov-report=html:coverage_html_instagram \
    -q

echo ""
echo "📁 Reporte HTML generado en: coverage_html_instagram/"
echo "📊 Para ver reporte detallado: open coverage_html_instagram/index.html"

# También generar para integration module
echo ""
echo "🔗 Ejecutando coverage para integration module..."
echo ""

$PYTHON -m pytest tests/ \
    --cov=src/integration \
    --cov-report=term-missing \
    -q

echo ""
echo "✅ Reportes de cobertura generados exitosamente"