#!/usr/bin/env python3
"""
DEBUG 2FA Instagram - Ver interfaz actual de 2FA

Este script abre Instagram, intenta login, y cuando pide 2FA
toma screenshot para ver qué botón usa Instagram actualmente.
NO intenta completar el 2FA.
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent / "instagram-upload"))

print("=" * 80)
print("🔍 DEBUG 2FA Instagram - Ver interfaz actual")
print("=" * 80)

async def debug_2fa():
    """Debug interfaz de 2FA de Instagram."""

    try:
        # Importar
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType

        # Configurar navegador VISIBLE
        config = BrowserConfig(
            headless=False,
            slow_mo=500,
            timeout=60000,
            browser_type=BrowserType.CHROMIUM
        )

        print("🖥️  Inicializando navegador...")
        browser_service = BrowserService(config)
        await browser_service.initialize()

        page = browser_service.page

        # Navegar a Instagram
        print("🌐 Navegando a Instagram...")
        await page.goto("https://www.instagram.com/", wait_until="networkidle")
        await asyncio.sleep(3)

        # Tomar screenshot inicial
        await page.screenshot(path="instagram_login_page.png", full_page=True)
        print("📸 Screenshot 1: instagram_login_page.png")

        # Intentar login manual (solo para llegar a 2FA)
        print("🔐 Intentando login para llegar a pantalla 2FA...")

        # Buscar campo email
        campo_email = await page.query_selector('input[name="email"]')
        if campo_email:
            print("✅ Campo email encontrado")
            await campo_email.fill("fiestacotoday")
        else:
            print("❌ Campo email NO encontrado")
            # Buscar alternativos
            campo_user = await page.query_selector('input[name="username"]')
            if campo_user:
                await campo_user.fill("fiestacotoday")
                print("✅ Campo username encontrado")

        # Buscar campo password
        campo_pass = await page.query_selector('input[name="pass"]')
        if campo_pass:
            print("✅ Campo password encontrado")
            await campo_pass.fill("RtiChUga0jI3x!D")
        else:
            campo_pass2 = await page.query_selector('input[name="password"]')
            if campo_pass2:
                await campo_pass2.fill("RtiChUga0jI3x!D")
                print("✅ Campo password (alternativo) encontrado")

        # Buscar botón de login
        print("🔍 Buscando botón de login...")
        boton_login = None

        # Probar varios selectores
        selectores = [
            'button:has-text("Log in")',
            'div[role="button"]:has-text("Log in")',
            'button[type="submit"]'
        ]

        for selector in selectores:
            try:
                boton = await page.query_selector(selector)
                if boton:
                    boton_login = boton
                    print(f"✅ Botón encontrado: {selector}")
                    break
            except:
                continue

        if boton_login:
            print("🖱️  Haciendo click en botón de login...")
            await boton_login.click()
        else:
            print("❌ No se encontró botón de login")

        # Esperar a que cargue pantalla de 2FA
        print("⏳ Esperando pantalla de 2FA (15 segundos)...")
        await asyncio.sleep(15)

        # Tomar screenshot de lo que haya
        await page.screenshot(path="instagram_2fa_page.png", full_page=True)
        print("📸 Screenshot 2: instagram_2fa_page.png")

        # Analizar página actual
        print("\n🔍 ANALIZANDO PÁGINA ACTUAL...")

        # Ver URL
        url = page.url
        print(f"   • URL actual: {url}")

        # Ver título
        titulo = await page.title()
        print(f"   • Título: {titulo}")

        # Ver todos los botones visibles
        print("\n🔘 BOTONES ENCONTRADOS:")
        todos_botones = await page.query_selector_all('button, div[role="button"], input[type="submit"]')

        for i, boton in enumerate(todos_botones[:10]):  # Mostrar primeros 10
            try:
                texto = await boton.text_content() or ""
                tipo = await boton.get_attribute('type') or "button/div"
                if texto.strip():
                    print(f"   {i+1}. '{texto.strip()}' ({tipo})")
            except:
                print(f"   {i+1}. [Error al leer botón]")

        # Ver campos de input
        print("\n📝 CAMPOS DE INPUT ENCONTRADOS:")
        todos_inputs = await page.query_selector_all('input')

        for i, inp in enumerate(todos_inputs[:10]):  # Mostrar primeros 10
            try:
                name = await inp.get_attribute('name') or "N/A"
                placeholder = await inp.get_attribute('placeholder') or "N/A"
                tipo = await inp.get_attribute('type') or "N/A"
                print(f"   {i+1}. name='{name}', type='{tipo}', placeholder='{placeholder}'")
            except:
                print(f"   {i+1}. [Error al leer input]")

        # Ver textos en página
        print("\n📋 TEXTO EN PÁGINA (fragmentos):")
        try:
            body_text = await page.text_content('body')
            lines = body_text.split('\n')
            for line in lines[:20]:  # Mostrar primeras 20 líneas
                line = line.strip()
                if line and len(line) > 10:
                    print(f"   • {line[:80]}...")
        except:
            print("   [Error al leer texto]")

        # Mantener navegador abierto para inspección manual
        print("\n" + "=" * 60)
        print("⚠️  NAVEGADOR MANTENIDO ABIERTO PARA INSPECCIÓN")
        print("=" * 60)
        print("\nINSTRUCCIONES:")
        print("1. Mira la ventana del navegador")
        print("2. ¿Ves pantalla de login o de 2FA?")
        print("3. ¿Qué botón ves para confirmar código?")
        print("4. ¿Dice 'Confirm', 'Submit', 'Verify', 'Continue'?")
        print("5. Presiona Enter en esta terminal cuando termines")

        input("\nPresiona Enter para cerrar navegador...")

        print("\n🧹 Cerrando navegador...")
        await browser_service.close()

        print("\n✅ DEBUG COMPLETADO")
        print("📄 Revisa los screenshots generados:")
        print("   • instagram_login_page.png")
        print("   • instagram_2fa_page.png")

        return True

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_2fa())