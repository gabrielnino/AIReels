#!/usr/bin/env python3
"""
Test simple de login para diagnóstico de 2FA.
Solo intenta login y muestra qué está pasando.
"""

import asyncio
import os
import sys
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))

async def test_login():
    """Test simple de login para diagnóstico."""

    print("🔧 TEST DE LOGIN - DIAGNÓSTICO")
    print("=" * 50)

    try:
        # Importar login manager
        from src.auth.login_manager import InstagramLoginManager

        # Crear instancia
        manager = InstagramLoginManager()
        print(f"✅ LoginManager creado")
        print(f"   • Usuario: {manager.username}")

        # Intentar login
        print("\n🔄 Intentando login...")
        success = await manager.login()

        if success:
            print("\n✅ ¡LOGIN EXITOSO!")
            print("   El login funcionó correctamente")
            return True
        else:
            print("\n❌ LOGIN FALLÓ")
            print("   Revisa el output anterior para ver qué pasó")
            return False

    except Exception as e:
        print(f"\n💥 ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""
    print("🚀 Iniciando test de diagnóstico de login...")
    print()

    success = await test_login()

    print("\n" + "=" * 50)
    print("📊 RESULTADO DEL DIAGNÓSTICO")
    print("=" * 50)

    if success:
        print("✅ Login funcionando correctamente")
        print("   Puedes ejecutar el upload completo")
    else:
        print("⚠️  Problemas con el login")
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("   1. Verifica credenciales en .env.instagram")
        print("   2. El código 2FA puede haber expirado")
        print("   3. Instagram puede estar mostrando captcha")
        print("   4. Revisa screenshots en ./logs/")

    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)