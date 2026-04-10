#!/usr/bin/env python3
"""
Fix para tests async con problemas de mocking.
Parte del ataque coordinado - Grupo A (Sam + Casey)
"""

import os
import re

def fix_async_mocking_issues():
    """Corregir issues de mocking en tests async."""
    print("🔧 FIX: ASYNC MOCKING ISSUES EN TESTS")
    print("=" * 50)

    test_file = "/home/luis/code/AIReels/instagram-upload/tests/unit/auth/test_browser_service.py"

    if not os.path.exists(test_file):
        print(f"❌ Archivo no encontrado: {test_file}")
        return

    with open(test_file, 'r') as f:
        content = f.read()

    # Fix 1: Corregir mock de playwright.async_api
    # Reemplazar imports problemáticos
    playwright_fixes = [
        # Patch incorrecto
        ("with patch\\('playwright.async_api.async_playwright'\\)", "with patch\\('src.auth.browser_service.async_playwright'\\)"),
        # También patch de playwright module
        (",\\s+patch\\('playwright'\\)", ""),  # Eliminar patch innecesario
    ]

    for old, new in playwright_fixes:
        if re.search(old, content):
            content = re.sub(old, new, content)
            print(f"   🔄 Fixed playwright patch: {old} → {new}")

    # Fix 2: Corregir AsyncMock usage con .first()
    # Los tests están usando locator() que devuelve AsyncMock, necesitan .first()
    async_test_fixes = [
        # test_is_element_visible_true
        (r'service\._page\.locator = Mock\(return_value=mock_element\)',
         r'service._page.locator.return_value.first.return_value = mock_element'),

        # test_is_element_visible_false
        (r'service\._page\.locator = Mock\(return_value=mock_element\)',
         r'service._page.locator.return_value.first.return_value = mock_element'),

        # test_get_element_text_found
        (r'service\._page\.locator = Mock\(return_value=mock_element\)',
         r'service._page.locator.return_value.first.return_value = mock_element'),

        # test_get_element_text_not_found
        (r'service\._page\.locator = Mock\(return_value=mock_element\)',
         r'service._page.locator.return_value.first.return_value = mock_element'),
    ]

    fixes_applied = 0
    for pattern, replacement in async_test_fixes:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes_applied += 1
            print(f"   🔄 Fixed AsyncMock pattern: {pattern[:50]}...")

    # También necesitamos asegurar que _page.locator es un Mock que tiene return_value.first
    # Añadir setup de locator como Mock con chain
    locator_setup = '''        service._page = AsyncMock()
        mock_locator = AsyncMock()
        service._page.locator = Mock(return_value=mock_locator)'''

    # Reemplazar ocurrencias simples
    simple_page_setup = r'service\._page = AsyncMock\(\)\s*\n\s*service\._page\.locator = Mock\(return_value=mock_element\)'
    if re.search(simple_page_setup, content):
        content = re.sub(simple_page_setup, locator_setup, content)
        print("   🔄 Fixed page.locator setup chain")

    # Guardar cambios
    with open(test_file, 'w') as f:
        f.write(content)

    print(f"\n✅ Fixes aplicados: {fixes_applied}")
    print(f"📄 Archivo actualizado: {test_file}")

    # Mostrar secciones corregidas
    print("\n🔍 SECCIONES CORREGIDAS:")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'locator.return_value.first' in line:
            context_start = max(0, i-2)
            context_end = min(len(lines), i+3)
            print(f"  Lines {context_start+1}-{context_end}:")
            for j in range(context_start, context_end):
                print(f"    {j+1}: {lines[j]}")
            print()

def create_async_test_helper():
    """Crear helper para tests async."""
    print("\n🔧 CREANDO HELPER PARA TESTS ASYNC")
    print("=" * 50)

    helper_content = '''"""
Helper functions for async testing.
"""
import asyncio
from unittest.mock import AsyncMock, Mock

def create_mock_browser_service():
    """Create a fully mocked BrowserService for testing."""
    mock_service = Mock()
    mock_service._is_initialized = True
    mock_service._page = AsyncMock()

    # Setup locator chain
    mock_locator = AsyncMock()
    mock_service._page.locator = Mock(return_value=mock_locator)

    return mock_service, mock_locator

def create_mock_element(is_visible=True, text=None):
    """Create a mocked element for testing."""
    mock_element = AsyncMock()

    if is_visible:
        mock_element.is_visible = AsyncMock(return_value=True)
    else:
        mock_element.is_visible = AsyncMock(side_effect=Exception("Not visible"))

    if text is not None:
        mock_element.text_content = AsyncMock(return_value=text)
    else:
        mock_element.text_content = AsyncMock(side_effect=Exception("Not found"))

    return mock_element

async def run_async_test(test_func):
    """Run async test function with proper event loop."""
    try:
        return await test_func()
    except Exception as e:
        print(f"Async test error: {e}")
        raise
'''

    helper_path = "/home/luis/code/AIReels/test_async_helper.py"
    with open(helper_path, 'w') as f:
        f.write(helper_content)

    print(f"✅ Helper creado: {helper_path}")

def test_fixes():
    """Probar que los fixes funcionan."""
    print("\n🧪 PROBANDO FIXES APLICADOS")
    print("=" * 50)

    import subprocess
    import sys

    test_file = "/home/luis/code/AIReels/instagram-upload/tests/unit/auth/test_browser_service.py"

    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        "-v",
        "--tb=short",
        "-k", "test_is_element_visible_true or test_is_element_visible_false or test_get_element_text"
    ]

    print(f"🔧 Ejecutando: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd="/home/luis/code/AIReels"
    )

    print("\n📊 RESULTADOS:")
    print(result.stdout)

    if result.stderr:
        print("\n❌ ERRORES:")
        print(result.stderr)

    print(f"\n📈 Exit code: {result.returncode}")

    if result.returncode == 0:
        print("✅ Tests de async funcionando después de fixes")
    else:
        print("⚠️  Algunos tests aún fallan, necesita más debugging")

def main():
    """Ejecutar todos los fixes."""
    print("🚀 APLICANDO FIXES PARA TESTS ASYNC - GRUPO A")
    print("=" * 60)

    fix_async_mocking_issues()
    create_async_test_helper()
    test_fixes()

    print("\n" + "=" * 60)
    print("✅ FIXES PARA TESTS ASYNC COMPLETADOS")
    print("📋 Siguiente: Ejecutar todos los tests de browser_service")

if __name__ == "__main__":
    main()