#!/usr/bin/env python3
"""
Corregir todos los imports en archivos de test.
Fase de consolidación del ataque coordinado.
"""

import os
import re
import sys
from pathlib import Path

def fix_imports_in_file(filepath):
    """Corregir imports en un archivo específico."""
    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content

    # Pattern para encontrar imports problemáticos de instagram_upload
    patterns = [
        # instagram_upload.src.auth.*
        (r'from instagram_upload\.src\.auth\.(\w+) import', r'from src.auth.\1 import'),
        (r'from instagram_upload\.src\.upload\.(\w+) import', r'from src.upload.\1 import'),

        # También capturar cualquier otro instagram_upload
        (r'instagram_upload\.src\.', 'src.'),
    ]

    fixes_applied = 0
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes_applied += 1

    # También añadir sys.path.insert si no está presente
    if fixes_applied > 0 and 'sys.path.insert' not in content:
        # Encontrar la primera línea después de imports
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                insert_index = i
                break

        # Insertar sys.path setup
        sys_path_code = '''import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))'''

        lines.insert(insert_index, sys_path_code)
        content = '\n'.join(lines)
        fixes_applied += 1

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return fixes_applied

    return 0

def find_test_files_with_import_issues():
    """Encontrar archivos de test con problemas de import."""
    project_root = Path("/home/luis/code/AIReels")

    test_files = []

    # Buscar en instagram-upload/tests/
    instagram_test_dir = project_root / "instagram-upload" / "tests"
    if instagram_test_dir.exists():
        for test_file in instagram_test_dir.rglob("test_*.py"):
            with open(test_file, 'r') as f:
                content = f.read()
                if 'instagram_upload' in content:
                    test_files.append(test_file)

    return test_files

def main():
    """Corregir todos los imports."""
    print("🔧 FASE DE CONSOLIDACIÓN: CORRIGIENDO TODOS LOS IMPORTS")
    print("=" * 60)

    test_files = find_test_files_with_import_issues()

    print(f"📁 Archivos con problemas de import encontrados: {len(test_files)}")

    total_fixes = 0
    fixed_files = []

    for test_file in test_files:
        print(f"\n📄 Procesando: {test_file.relative_to(Path('/home/luis/code/AIReels'))}")

        fixes = fix_imports_in_file(test_file)

        if fixes > 0:
            total_fixes += fixes
            fixed_files.append(test_file)
            print(f"   ✅ {fixes} fixes aplicados")
        else:
            print(f"   ⏭️  Sin cambios necesarios")

    print(f"\n" + "=" * 60)
    print(f"📊 RESUMEN:")
    print(f"   • Archivos procesados: {len(test_files)}")
    print(f"   • Archivos corregidos: {len(fixed_files)}")
    print(f"   • Total fixes aplicados: {total_fixes}")

    if fixed_files:
        print(f"\n✅ ARCHIVOS CORREGIDOS:")
        for f in fixed_files:
            print(f"   • {f.relative_to(Path('/home/luis/code/AIReels'))}")

    # Crear también un conftest.py en instagram-upload/tests/
    print(f"\n🔧 CREANDO conftest.py PARA INSTAGRAM-UPLOAD")
    conftest_content = '''"""
Pytest configuration for instagram-upload tests.
"""
import sys
import os
from pathlib import Path

# Setup paths
test_dir = Path(__file__).parent
module_root = test_dir.parent
project_root = module_root.parent

sys.path.insert(0, str(module_root))
sys.path.insert(0, str(project_root))

print(f"🔧 Pytest config for instagram-upload tests")
print(f"📁 Module root: {module_root}")
'''

    conftest_path = Path("/home/luis/code/AIReels/instagram-upload/tests/conftest.py")
    conftest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(conftest_path, 'w') as f:
        f.write(conftest_content)

    print(f"✅ conftest.py creado en: {conftest_path}")

    print(f"\n" + "=" * 60)
    print(f"🚀 EJECUTAR TESTS COMPLETOS:")
    print(f"   ./run_tests_fixed.sh instagram")
    print(f"\n📋 Verificar que todos los imports funcionan correctamente.")

if __name__ == "__main__":
    main()