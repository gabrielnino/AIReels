#!/usr/bin/env python3
"""
TEST UPLOAD SIMPLE - Versión mínima para probar login
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))

print("=" * 80)
print("🚀 TEST UPLOAD SIMPLE")
print("=" * 80)

async def test_login():
    """Probar solo el login."""

    try:
        from dotenv import load_dotenv
        env_path = current_dir / "instagram-upload" / ".env.instagram"
        load_dotenv(str(env_path))

        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')

        print(f"✅ Usuario: {username}")

        # Importar browser service
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType

        config = BrowserConfig(
            headless=True,  # Modo headless para pruebas
            slow_mo=100,
            timeout=60000,
            browser_type=BrowserType.CHROMIUM
        )

        browser_service = BrowserService(config)

        print("🖥️  Inicializando navegador...")
        await browser_service.initialize()
        page = browser_service.page

        # Navegar a Instagram
        print("🌐 Navegando a Instagram...")
        await page.goto('https://www.instagram.com/')
        await asyncio.sleep(3)

        # Verificar si ya estamos logueados
        current_url = page.url
        print(f"ℹ️  URL actual: {current_url}")

        if "/accounts/login" not in current_url:
            print("✅ Ya estamos logueados!")
            return True

        # Intentar login
        print("🔐 Intentando login...")

        # Buscar campo de username
        username_selectors = [
            'input[name="email"]',
            'input[name="username"]',
            'input[aria-label="Phone number, username, or email"]'
        ]

        username_filled = False
        for selector in username_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.fill(selector, username)
                print(f"✅ Username: {selector}")
                username_filled = True
                break
            except:
                continue

        if not username_filled:
            print("❌ No se encontró campo de username")
            return False

        # Buscar campo de password
        password_selectors = [
            'input[name="pass"]',
            'input[name="password"]',
            'input[aria-label="Password"]'
        ]

        password_filled = False
        for selector in password_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.fill(selector, password)
                print(f"✅ Password: {selector}")
                password_filled = True
                break
            except:
                continue

        if not password_filled:
            print("❌ No se encontró campo de password")
            return False

        # Buscar botón de login
        login_button_selectors = [
            'button[type="submit"]',
            'div[role="button"]:has-text("Log in")',
            'button:has-text("Log in")'
        ]

        login_clicked = False
        for selector in login_button_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                print(f"✅ Login button: {selector}")
                login_clicked = True
                break
            except:
                continue

        if not login_clicked:
            print("❌ No se encontró botón de login")
            return False

        # Esperar login
        print("⏳ Esperando login...")
        await asyncio.sleep(5)

        # Verificar login
        current_url = page.url
        print(f"ℹ️  URL después de login: {current_url}")

        if "/accounts/login" not in current_url:
            print("✅ Login exitoso!")

            # Verificar popup de notificaciones
            print("🔍 Buscando popup de notificaciones...")
            await asyncio.sleep(2)

            # Buscar botón "Not Now"
            not_now_selectors = [
                'button:has-text("Not Now")',
                'button:has-text("Not now")',
                'div[role="button"]:has-text("Not Now")'
            ]

            for selector in not_now_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=3000):
                        print(f"⚠️  Popup encontrado: {selector}")
                        await element.click()
                        print("✅ Click en 'Not Now'")
                        await asyncio.sleep(2)
                        break
                except:
                    continue

            return True
        else:
            print("❌ Login falló - aún en página de login")
            return False

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""
    print("🚀 Iniciando test de login...")
    success = await test_login()

    print("\n" + "=" * 80)
    print("🏁 RESULTADO")
    print("=" * 80)

    if success:
        print("✅ ¡TEST EXITOSO!")
        print("✅ Login funcionando")
        print("✅ Popup de notificaciones manejado")
    else:
        print("❌ TEST FALLÓ")

    # Mantener navegador abierto
    print("\n⚠️  Navegador mantenido abierto para inspección")
    print("⚠️  Presiona Ctrl+C para cerrar")

    try:
        await asyncio.sleep(10)  # Mantener abierto por 10 segundos
        print("\n👋 Cerrando navegador...")
    except KeyboardInterrupt:
        print("\n👋 Cerrando...")

if __name__ == "__main__":
    asyncio.run(main())