#!/usr/bin/env python3
"""
Prueba de selectores para Instagram - SOLO DIAGNÓSTICO

Este script prueba si los selectores CSS actualizados funcionan
con la interfaz actual de Instagram.

NO hace login real, NO sube videos, NO publica nada.
Solo verifica la estructura de la página.
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent / "instagram-upload"))

print("=" * 80)
print("🔍 PRUEBA DE SELECTORES - Instagram UI Diagnosis")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def probar_selectores():
    """Probar selectores en Instagram sin acciones reales."""

    print("🎯 OBJETIVO: Verificar si los selectores funcionan con Instagram actual")
    print("⚠️  ADVERTENCIA: No se harán acciones reales, solo diagnóstico")
    print()

    try:
        # 1. Importar módulos
        print("1. 📦 IMPORTANDO MÓDULOS...")
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        print("✅ Módulos importados")

        # 2. Configurar navegador VISIBLE
        print("\n2. ⚙️  CONFIGURANDO NAVEGADOR...")
        config = BrowserConfig(
            headless=False,      # VISIBLE para ver qué pasa
            slow_mo=500,         # Pausa para ver mejor
            timeout=60000,       # 60 segundos timeout
            browser_type=BrowserType.CHROMIUM
        )

        print(f"✅ Navegador configurado:")
        print(f"   • Headless: {config.headless} (VISIBLE)")
        print(f"   • Slow mo: {config.slow_mo}ms")

        # 3. Inicializar navegador
        print("\n3. 🔓 INICIALIZANDO NAVEGADOR...")
        browser_service = BrowserService(config)
        await browser_service.initialize()

        print("✅ Navegador inicializado")
        print("   • Se abrirá Chrome/Chromium")
        print("   • Puedes ver todo el proceso")

        await asyncio.sleep(3)  # Esperar a que el navegador se abra

        # 4. Navegar a Instagram
        print("\n4. 🌐 NAVEGANDO A INSTAGRAM.COM...")
        page = await browser_service.get_page()

        print("   • Cargando https://www.instagram.com/")
        await page.goto("https://www.instagram.com/", wait_until="networkidle")

        print("✅ Instagram cargado")
        await asyncio.sleep(5)  # Esperar a que cargue completamente

        # 5. Tomar screenshot inicial
        print("\n5. 📸 TOMANDO SCREENSHOT INICIAL...")
        screenshot_path = "instagram_landing_page.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot guardado: {screenshot_path}")

        # 6. Probar selectores de username
        print("\n6. 🔍 PROBANDO SELECTORES DE USERNAME...")
        username_selectors = [
            'input[name="username"]',
            'input[aria-label="Phone number, username, or email"]',
            'input[aria-label*="username"]',
            'input[placeholder*="username"]',
            'input[placeholder*="Username"]',
            'input[type="text"]:first-of-type',
            'input:first-of-type'
        ]

        username_encontrado = False
        for i, selector in enumerate(username_selectors, 1):
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"   ✅ Selector {i}: '{selector}' - ENCONTRADO")
                    username_encontrado = True

                    # Ver algunas propiedades
                    placeholder = await element.get_attribute('placeholder') or 'N/A'
                    name = await element.get_attribute('name') or 'N/A'
                    aria_label = await element.get_attribute('aria-label') or 'N/A'

                    print(f"      • Placeholder: {placeholder}")
                    print(f"      • Name: {name}")
                    print(f"      • Aria-label: {aria_label}")
                else:
                    print(f"   ❌ Selector {i}: '{selector}' - NO ENCONTRADO")
            except Exception as e:
                print(f"   ❌ Selector {i}: '{selector}' - ERROR: {e}")

        # 7. Probar selectores de password
        print("\n7. 🔍 PROBANDO SELECTORES DE PASSWORD...")
        password_selectors = [
            'input[name="password"]',
            'input[aria-label="Password"]',
            'input[aria-label*="password"]',
            'input[placeholder*="password"]',
            'input[placeholder*="Password"]',
            'input[type="password"]',
            'input:nth-of-type(2)'
        ]

        password_encontrado = False
        for i, selector in enumerate(password_selectors, 1):
            try:
                element = await page.query_selector(selector)
                if element:
                    print(f"   ✅ Selector {i}: '{selector}' - ENCONTRADO")
                    password_encontrado = True

                    # Ver algunas propiedades
                    placeholder = await element.get_attribute('placeholder') or 'N/A'
                    name = await element.get_attribute('name') or 'N/A'
                    aria_label = await element.get_attribute('aria-label') or 'N/A'
                    type_attr = await element.get_attribute('type') or 'N/A'

                    print(f"      • Placeholder: {placeholder}")
                    print(f"      • Name: {name}")
                    print(f"      • Aria-label: {aria_label}")
                    print(f"      • Type: {type_attr}")
                else:
                    print(f"   ❌ Selector {i}: '{selector}' - NO ENCONTRADO")
            except Exception as e:
                print(f"   ❌ Selector {i}: '{selector}' - ERROR: {e}")

        # 8. Probar selectores de botón de login
        print("\n8. 🔍 PROBANDO SELECTORES DE BOTÓN DE LOGIN...")
        login_button_selectors = [
            'button[type="submit"]',
            'div[role="button"]:has-text("Log in")',
            'button:has-text("Log in")',
            'button:has-text("Log In")'
        ]

        login_encontrado = False
        for i, selector in enumerate(login_button_selectors, 1):
            try:
                if 'has-text' in selector:
                    # Selector especial con texto
                    elements = await page.query_selector_all('button, div[role="button"]')
                    found = False
                    for elem in elements:
                        text = await elem.text_content() or ''
                        if 'log in' in text.lower():
                            print(f"   ✅ Selector {i}: '{selector}' - ENCONTRADO (texto: '{text.strip()}')")
                            login_encontrado = True
                            found = True
                            break
                    if not found:
                        print(f"   ❌ Selector {i}: '{selector}' - NO ENCONTRADO")
                else:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content() or 'N/A'
                        print(f"   ✅ Selector {i}: '{selector}' - ENCONTRADO (texto: '{text.strip()}')")
                        login_encontrado = True
                    else:
                        print(f"   ❌ Selector {i}: '{selector}' - NO ENCONTRADO")
            except Exception as e:
                print(f"   ❌ Selector {i}: '{selector}' - ERROR: {e}")

        # 9. Analizar estructura de la página
        print("\n9. 📊 ANALIZANDO ESTRUCTURA DE LA PÁGINA...")

        # Contar elementos
        all_inputs = await page.query_selector_all('input')
        all_buttons = await page.query_selector_all('button')
        all_forms = await page.query_selector_all('form')

        print(f"   • Inputs totales: {len(all_inputs)}")
        print(f"   • Buttons totales: {len(all_buttons)}")
        print(f"   • Forms totales: {len(all_forms)}")

        # Mostrar primeros 3 inputs
        print("\n   Primeros 3 inputs encontrados:")
        for i, inp in enumerate(all_inputs[:3], 1):
            try:
                placeholder = await inp.get_attribute('placeholder') or 'N/A'
                name = await inp.get_attribute('name') or 'N/A'
                type_attr = await inp.get_attribute('type') or 'N/A'
                aria_label = await inp.get_attribute('aria-label') or 'N/A'

                print(f"   Input {i}:")
                print(f"      • Placeholder: {placeholder}")
                print(f"      • Name: {name}")
                print(f"      • Type: {type_attr}")
                print(f"      • Aria-label: {aria_label}")
            except:
                print(f"   Input {i}: Error al obtener atributos")

        # 10. Resumen de diagnóstico
        print("\n10. 📋 RESUMEN DE DIAGNÓSTICO")
        print("-" * 50)

        if username_encontrado and password_encontrado and login_encontrado:
            print("✅ ¡TODOS LOS SELECTORES FUNCIONAN!")
            print("   • Campos de username: ENCONTRADOS")
            print("   • Campos de password: ENCONTRADOS")
            print("   • Botón de login: ENCONTRADO")
            print("\n💡 El login automático DEBERÍA funcionar")
        else:
            print("⚠️  ALGUNOS SELECTORES NO FUNCIONAN")
            if not username_encontrado:
                print("   • Campos de username: NO ENCONTRADOS")
            if not password_encontrado:
                print("   • Campos de password: NO ENCONTRADOS")
            if not login_encontrado:
                print("   • Botón de login: NO ENCONTRADO")

            print("\n🔧 Posibles soluciones:")
            print("   1. Instagram cambió su interfaz")
            print("   2. Necesita selectores diferentes")
            print("   3. Hay un popup/cookie banner bloqueando")
            print("   4. La página no cargó completamente")

        # 11. Cerrar navegador
        print("\n11. 🧹 CERRANDO NAVEGADOR...")
        await asyncio.sleep(5)  # Esperar para que el usuario vea
        await browser_service.close()

        print("✅ Navegador cerrado")
        print("\n🎉 PRUEBA DE DIAGNÓSTICO COMPLETADA")

        return True

    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en prueba: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""

    inicio = time.time()
    print("🔍 Iniciando prueba de diagnóstico de selectores...")
    print()

    success = await probar_selectores()
    fin = time.time()

    duracion = fin - inicio

    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL DE PRUEBA")
    print("=" * 80)

    if success:
        print("✅ PRUEBA DE DIAGNÓSTICO COMPLETADA")
        print(f"\n⏱️  Duración total: {duracion:.1f} segundos")

        print("\n📄 ARCHIVOS GENERADOS:")
        print("   • instagram_landing_page.png - Screenshot de la página")

        print("\n💡 RECOMENDACIONES:")
        print("   1. Revisa el screenshot para ver la interfaz actual")
        print("   2. Verifica los selectores que funcionaron")
        print("   3. Ajusta selectores si es necesario")
    else:
        print("⚠️  PRUEBA CON ERRORES")
        print(f"\n⏱️  Duración: {duracion:.1f} segundos")

    print(f"\n⏰ Fin: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())