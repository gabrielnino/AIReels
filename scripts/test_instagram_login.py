#!/usr/bin/env python3
"""
Script de prueba para login de Instagram con Playwright.
Maneja autenticación de dos factores (2FA) con entrada manual.
Solo para desarrollo - NO usar en producción sin revisión.
"""
import asyncio
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar configuración
load_dotenv('.env.instagram')

async def test_instagram_login():
    """Prueba de login a Instagram con soporte para 2FA."""
    from playwright.async_api import async_playwright

    print("🔐 Probando login de Instagram...")
    print("================================")

    async with async_playwright() as p:
        # Configurar browser
        browser = await p.chromium.launch(
            headless=os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true',
            slow_mo=int(os.getenv('PLAYWRIGHT_SLOW_MO', '100'))
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = await context.new_page()

        try:
            # Navegar a Instagram
            print("🌐 Navegando a Instagram...")
            await page.goto('https://www.instagram.com/')
            await page.wait_for_timeout(2000)

            # Aceptar cookies si aparece
            try:
                accept_button = page.get_by_role("button", name="Allow all cookies")
                if await accept_button.is_visible(timeout=3000):
                    await accept_button.click()
                    print("✅ Cookies aceptadas")
                    await page.wait_for_timeout(1000)
            except:
                pass  # No hay popup de cookies

            # Ingresar credenciales
            print("📝 Ingresando credenciales...")
            username = os.getenv('INSTAGRAM_USERNAME')
            password = os.getenv('INSTAGRAM_PASSWORD')

            if not username or not password:
                print("❌ Credenciales no configuradas en .env.instagram")
                print("   Completar INSTAGRAM_USERNAME e INSTAGRAM_PASSWORD")
                return False

            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)

            # Click en login
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)

            # Verificar login exitoso o 2FA
            await page.wait_for_timeout(3000)

            # Caso 1: Login exitoso (sin 2FA)
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
                print("✅ Login exitoso (sin 2FA)")

                # Guardar cookies para futuras sesiones
                cookies_path = os.getenv('INSTAGRAM_COOKIES_PATH', './data/instagram_cookies.json')
                Path(cookies_path).parent.mkdir(parents=True, exist_ok=True)

                cookies = await context.cookies()
                with open(cookies_path, 'w') as f:
                    json.dump(cookies, f)
                print(f"💾 Cookies guardadas en: {cookies_path}")

                await browser.close()
                return True
            except:
                pass  # No se encontró home, podría ser 2FA

            # Caso 2: 2FA requerido
            try:
                # Buscar campo de código 2FA
                await page.wait_for_selector('input[name="verificationCode"]', timeout=5000)
                print("")
                print("⚠️  AUTENTICACIÓN DE DOS FACTORES (2FA) REQUERIDA")
                print("==================================================")
                print("Se ha enviado un código de 6 dígitos a tu dispositivo")
                print("")
                print("🔢 POR FAVOR INGRESA EL CÓDIGO 2FA")
                print("----------------------------------")
                print("1. Revisa tu app de autenticación o SMS")
                print("2. Ingresa el código de 6 dígitos a continuación")
                print("3. Presiona Enter")
                print("")

                # Leer código del usuario
                if sys.stdin.isatty():
                    # Terminal interactivo
                    code = input("📱 Código 2FA (6 dígitos): ").strip()
                else:
                    # No interactivo, usar variable de entorno
                    code = os.getenv('INSTAGRAM_2FA_CODE', '')
                    if not code:
                        print("❌ No se puede solicitar código 2FA en modo no interactivo")
                        print("   Configurar INSTAGRAM_2FA_CODE en .env.instagram")
                        await browser.close()
                        return False

                # Validar código
                if len(code) != 6 or not code.isdigit():
                    print(f"❌ Código inválido: '{code}'. Debe ser exactamente 6 dígitos.")
                    await page.screenshot(path='./logs/2fa_invalid_code.png')
                    await browser.close()
                    return False

                # Ingresar código 2FA
                print(f"🔑 Ingresando código: {'*' * 6}")
                await page.fill('input[name="verificationCode"]', code)

                # Buscar y hacer click en botón de confirmación
                confirm_button = page.locator('button:has-text("Confirm")').first
                await confirm_button.click()

                await page.wait_for_timeout(3000)

                # Verificar si 2FA fue exitoso
                try:
                    await page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
                    print("✅ 2FA exitoso, login completado")

                    # Guardar cookies
                    cookies_path = os.getenv('INSTAGRAM_COOKIES_PATH', './data/instagram_cookies.json')
                    cookies = await context.cookies()
                    with open(cookies_path, 'w') as f:
                        json.dump(cookies, f)
                    print(f"💾 Cookies guardadas en: {cookies_path}")

                    await browser.close()
                    return True
                except:
                    # Verificar si hay error específico
                    try:
                        error_elem = page.locator('[data-testid="error-alert"]').first
                        error_text = await error_elem.text_content(timeout=2000)
                        print(f"❌ Error en 2FA: {error_text}")
                    except:
                        print("❌ Código 2FA incorrecto o expirado")

                    await page.screenshot(path='./logs/2fa_error.png')
                    print("📸 Screenshot guardado en ./logs/2fa_error.png")
                    await browser.close()
                    return False

            except Exception as e:
                print(f"❌ No se pudo encontrar campo 2FA: {e}")
                await page.screenshot(path='./logs/2fa_not_found.png')
                await browser.close()
                return False

        except Exception as e:
            print(f"❌ Error durante login: {e}")
            await page.screenshot(path='./logs/login_exception.png')
            print("📸 Screenshot guardado en ./logs/login_exception.png")
            await browser.close()
            return False

def main():
    """Función principal."""
    # Verificar que existe .env.instagram
    if not Path('.env.instagram').exists():
        print("❌ Archivo .env.instagram no encontrado")
        print("   Ejecutar: ./scripts/setup_instagram_config.sh primero")
        return 1

    # Verificar credenciales
    load_dotenv('.env.instagram')
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    if not username or username == 'your_instagram_username_here':
        print("❌ INSTAGRAM_USERNAME no configurado en .env.instagram")
        return 1

    if not password or password == 'your_instagram_password_here':
        print("❌ INSTAGRAM_PASSWORD no configurado en .env.instagram")
        return 1

    print(f"👤 Usuario configurado: {username}")
    print(f"🔐 Contraseña: {'*' * len(password)}")
    print("")

    # Ejecutar prueba
    success = asyncio.run(test_instagram_login())

    if success:
        print("")
        print("🎉 PRUEBA DE LOGIN EXITOSA")
        print("==========================")
        print("La configuración de Instagram es correcta.")
        print("Las cookies de sesión han sido guardadas.")
        print("")
        print("✅ Puedes proceder con el desarrollo del upload service.")
        return 0
    else:
        print("")
        print("💀 PRUEBA DE LOGIN FALLIDA")
        print("==========================")
        print("Revisa los siguientes puntos:")
        print("1. Credenciales correctas en .env.instagram")
        print("2. Conexión a internet estable")
        print("3. Instagram no está bloqueando el acceso")
        print("4. Código 2FA válido y no expirado")
        print("")
        print("📁 Revisa los screenshots en ./logs/ para debugging")
        return 1

if __name__ == "__main__":
    exit(main())