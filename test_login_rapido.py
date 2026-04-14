#!/usr/bin/env python3
"""
TEST DE LOGIN RÁPIDO - Verificar si las credenciales funcionan
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar configuración
current_dir = Path(__file__).parent
env_path = current_dir / "instagram-upload" / ".env.instagram"
load_dotenv(str(env_path))

username = os.environ.get('INSTAGRAM_USERNAME')
password = os.environ.get('INSTAGRAM_PASSWORD')

print("=" * 60)
print("🔐 TEST DE LOGIN RÁPIDO")
print("=" * 60)
print(f"Usuario: {username}")
print(f"Password: {'*' * len(password) if password else 'NO CONFIGURADO'}")
print()

async def test_login():
    """Probar login rápidamente."""

    # Importar solo lo necesario
    import sys
    sys.path.insert(0, str(current_dir / "instagram-upload"))

    from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType

    # Configurar navegador RÁPIDO
    config = BrowserConfig(
        headless=False,
        slow_mo=100,  # Más rápido
        timeout=60000,
        browser_type=BrowserType.CHROMIUM
    )

    browser_service = BrowserService(config)

    try:
        await browser_service.initialize()
        page = browser_service.page

        print("🌐 Navegando a Instagram...")
        await page.goto('https://www.instagram.com/')
        await asyncio.sleep(2)

        print("📝 Ingresando credenciales...")

        # Intentar username
        try:
            await page.fill('input[name="email"]', username)
            print("✅ Username ingresado")
        except:
            try:
                await page.fill('input[name="username"]', username)
                print("✅ Username ingresado (alternativo)")
            except Exception as e:
                print(f"❌ Error con username: {e}")
                return False

        # Intentar password
        try:
            await page.fill('input[name="pass"]', password)
            print("✅ Password ingresado")
        except:
            try:
                await page.fill('input[name="password"]', password)
                print("✅ Password ingresado (alternativo)")
            except Exception as e:
                print(f"❌ Error con password: {e}")
                return False

        await asyncio.sleep(1)

        print("🖱️  Haciendo click en botón de login...")

        # Intentar diferentes botones
        button_selectors = [
            'button[type="submit"]',
            'div[role="button"]',
            'button:has-text("Log in")',
            'button:has-text("Log In")'
        ]

        for selector in button_selectors:
            try:
                await page.click(selector)
                print(f"✅ Click en: {selector}")
                break
            except:
                continue

        print("⏳ Esperando respuesta de login (10 segundos)...")
        await asyncio.sleep(10)

        # Verificar si login fue exitoso
        try:
            await page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
            print("✅ ✅ ✅ LOGIN EXITOSO!")
            print("✅ Estás en la página principal de Instagram")
            return True
        except:
            print("⚠️  No se pudo verificar login automáticamente")

            # Verificar si hay mensaje de error
            try:
                error_element = await page.wait_for_selector('div:has-text("error"), div:has-text("Error"), div:has-text("incorrect")', timeout=3000)
                error_text = await error_element.text_content()
                print(f"❌ Error detectado: {error_text[:100]}...")
                return False
            except:
                print("ℹ️  No se detectó mensaje de error específico")

            # Verificar URL actual
            current_url = page.url
            print(f"📄 URL actual: {current_url}")

            if "challenge" in current_url or "login" in current_url:
                print("❌ Parece que hay un problema con el login (CAPTCHA o verificación)")
                return False
            else:
                print("⚠️  No está claro si el login fue exitoso")
                print("   Revisa manualmente la página del navegador")
                return True

    except Exception as e:
        print(f"❌ Error durante test: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        print("\n⚠️  Navegador mantenido abierto para verificación manual")
        print("   Cierra el navegador cuando hayas terminado")

async def main():
    """Función principal."""

    if not username or not password:
        print("❌ Credenciales no configuradas en .env.instagram")
        return False

    success = await test_login()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEST COMPLETADO - Login posiblemente exitoso")
        print("   Verifica manualmente en el navegador")
    else:
        print("❌ TEST FALLÓ - Problemas con el login")
        print("   Revisa:")
        print("   1. Credenciales en .env.instagram")
        print("   2. Si 2FA está deshabilitado")
        print("   3. Conexión a internet")
        print("   4. Si Instagram muestra CAPTCHA")

    return success

if __name__ == "__main__":
    asyncio.run(main())