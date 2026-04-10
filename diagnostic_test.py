#!/usr/bin/env python3
"""
Diagnóstico de tests fallidos para ataque coordinado.
Focus en root causes específicas.
"""

import sys
import os
import subprocess
import traceback

def diagnose_import_issues():
    """Diagnóstico de problemas de importación."""
    print("🔍 DIAGNÓSTICO DE IMPORT ISSUES")
    print("=" * 50)

    test_dirs = [
        "instagram-upload/tests/unit/auth",
        "instagram-upload/tests/unit/upload",
        "qwen-poc/tests/unit"
    ]

    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            print(f"\n📁 Examinando: {test_dir}")
            for filename in os.listdir(test_dir):
                if filename.startswith("test_") and filename.endswith(".py"):
                    filepath = os.path.join(test_dir, filename)
                    print(f"  📄 {filename}")

                    # Verificar imports básicos
                    with open(filepath, 'r') as f:
                        content = f.read()

                    # Buscar imports problemáticos
                    issues = []
                    if "from src." in content:
                        issues.append("Usa 'from src.' - puede necesitar sys.path ajust")
                    if "playwright" in content and "mock" not in content.lower():
                        issues.append("Usa playwright sin mocking")
                    if "asyncio" in content and "pytest.mark.asyncio" not in content:
                        issues.append("Async sin decorator pytest.mark.asyncio")

                    if issues:
                        print(f"    ⚠️  Posibles issues: {', '.join(issues)}")

def diagnose_specific_test(test_file, test_name=None):
    """Diagnóstico de test específico."""
    print(f"\n🎯 DIAGNÓSTICO ESPECÍFICO: {test_file}")
    print("=" * 50)

    if not os.path.exists(test_file):
        print(f"❌ Archivo no encontrado: {test_file}")
        return

    # Configurar python path
    env = os.environ.copy()
    project_root = "/home/luis/code/AIReels"
    env['PYTHONPATH'] = f"{project_root}:{project_root}/instagram-upload:{project_root}/qwen-poc"

    # Construir comando pytest
    cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
    if test_name:
        cmd.extend(["-k", test_name])

    print(f"🔧 Comando: {' '.join(cmd)}")
    print(f"📁 CWD: {os.getcwd()}")
    print(f"🐍 Python: {sys.executable}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=project_root
        )

        print("\n📤 OUTPUT:")
        print(result.stdout[:1000])

        if result.stderr:
            print("\n❌ STDERR:")
            print(result.stderr[:500])

        print(f"\n📊 Exit code: {result.returncode}")

    except Exception as e:
        print(f"\n💥 Error ejecutando test: {e}")
        traceback.print_exc()

def create_test_env_file():
    """Crear archivo .env.test para testing."""
    print("\n🔧 CREANDO .env.test PARA TESTING")
    print("=" * 50)

    env_content = """# Test environment variables for Instagram Upload Service
# ⚠️ NOT FOR PRODUCTION ⚠️

# Instagram Credentials (test account)
INSTAGRAM_USERNAME=test_user
INSTAGRAM_PASSWORD=test_password_123

# Playwright Configuration
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_SLOW_MO=0
PLAYWRIGHT_TIMEOUT=10000

# Instagram Configuration
INSTAGRAM_ENABLE_2FA=false
INSTAGRAM_MAX_VIDEO_SIZE_MB=100
INSTAGRAM_ALLOWED_FORMATS=mp4,mov
INSTAGRAM_MAX_VIDEO_DURATION_SEC=90

# Upload Configuration
INSTAGRAM_UPLOAD_TIMEOUT=30
INSTAGRAM_UPLOAD_MAX_RETRIES=2
INSTAGRAM_PUBLISH_TIMEOUT=10
INSTAGRAM_DRY_RUN=true  # Important for tests!

# Paths
INSTAGRAM_VIDEO_INPUT_DIR=/tmp/test_videos/input
INSTAGRAM_VIDEO_PROCESSED_DIR=/tmp/test_videos/processed
INSTAGRAM_VIDEO_FAILED_DIR=/tmp/test_videos/failed

# Browser Configuration
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1024
BROWSER_VIEWPORT_HEIGHT=768

# Test-specific flags
TEST_MODE=true
SKIP_BROWSER_LAUNCH=true
MOCK_EXTERNAL_APIS=true
"""

    env_path = "/home/luis/code/AIReels/.env.test"
    with open(env_path, 'w') as f:
        f.write(env_content)

    print(f"✅ Archivo creado: {env_path}")
    print("📝 Variables configuradas para testing seguro")

    # También crear en instagram-upload
    ig_env_path = "/home/luis/code/AIReels/instagram-upload/.env.test"
    with open(ig_env_path, 'w') as f:
        f.write(env_content)

    print(f"✅ También creado: {ig_env_path}")

def main():
    """Ejecutar diagnóstico completo."""
    print("🚀 EJECUTANDO DIAGNÓSTICO PARA ATAQUE COORDINADO")
    print("=" * 60)

    # 1. Diagnóstico de imports
    diagnose_import_issues()

    # 2. Crear entorno de testing
    create_test_env_file()

    print("\n" + "=" * 60)
    print("🎯 TESTS CRÍTICOS PARA DIAGNÓSTICO INMEDIATO:")
    print("1. instagram-upload/tests/unit/auth/test_browser_service.py")
    print("2. instagram-upload/tests/unit/auth/test_login_manager.py")
    print("3. instagram-upload/tests/unit/upload/test_video_uploader.py")

    print("\n⚡ EJECUTANDO DIAGNÓSTICO DE TESTS CRÍTICOS...")

    # Diagnóstico de tests específicos
    critical_tests = [
        "instagram-upload/tests/unit/auth/test_browser_service.py",
        "instagram-upload/tests/unit/auth/test_login_manager.py",
        "instagram-upload/tests/unit/upload/test_video_uploader.py"
    ]

    for test_file in critical_tests:
        full_path = f"/home/luis/code/AIReels/{test_file}"
        diagnose_specific_test(full_path)

        # Pausa entre tests
        print("\n" + "-" * 50 + "\n")

    print("✅ DIAGNÓSTICO COMPLETADO")
    print("📋 Siguientes pasos:")
    print("1. Revisar root causes identificadas")
    print("2. Aplicar fixes según diagnóstico")
    print("3. Re-ejecutar tests con .env.test")

if __name__ == "__main__":
    main()