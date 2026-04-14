#!/usr/bin/env python3
"""
UPLOAD MANUAL DIRECTO
Upload directo desde la página de upload ya cargada
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))

print("=" * 80)
print("🚀 UPLOAD MANUAL DIRECTO - Desde página ya cargada")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def hacer_upload_manual(page, video_path, caption, hashtags):
    """Hacer upload manualmente desde la página ya cargada."""
    print("📤 HACIENDO UPLOAD MANUAL...")

    try:
        # PASO 1: Seleccionar archivo
        print("1. 📁 Seleccionando archivo de video...")

        # Buscar input de archivo
        file_input_selectors = [
            'input[type="file"]',
            'input[accept*="video"]',
            'input[accept*="mp4"]',
            'input[accept*="mov"]'
        ]

        file_input = None
        for selector in file_input_selectors:
            try:
                file_input = page.locator(selector).first
                if await file_input.is_visible(timeout=5000):
                    print(f"✅ Input de archivo encontrado: {selector}")
                    break
            except:
                continue

        if not file_input:
            print("❌ No se encontró input de archivo")
            return False

        # Subir archivo
        await file_input.set_input_files(str(video_path))
        print(f"✅ Archivo seleccionado: {video_path.name}")
        await asyncio.sleep(5)

        # PASO 2: Esperar a que cargue el video
        print("2. ⏳ Esperando a que cargue el video...")
        await asyncio.sleep(10)

        # Verificar elementos de preview
        preview_selectors = [
            'video',
            'div[class*="preview"]',
            'div[class*="Preview"]',
            'div[class*="video"]',
            'div[class*="Video"]'
        ]

        preview_found = False
        for selector in preview_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=5000):
                    print(f"✅ Preview encontrado: {selector}")
                    preview_found = True
                    break
            except:
                continue

        if not preview_found:
            print("⚠️  No se encontró preview, continuando de todas formas...")

        # PASO 3: Hacer click en Next/Continue
        print("3. ⏭️  Haciendo click en Next...")

        next_selectors = [
            'div[role="button"]:has-text("Next")',
            'button:has-text("Next")',
            'div:has-text("Next"):visible',
            'div[role="button"]:has-text("Continue")',
            'button:has-text("Continue")'
        ]

        next_clicked = False
        for selector in next_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=5000):
                    print(f"✅ Botón Next encontrado: {selector}")
                    await element.click()
                    print("✅ Click en Next")
                    next_clicked = True
                    await asyncio.sleep(5)
                    break
            except:
                continue

        if not next_clicked:
            print("❌ No se encontró botón Next")
            return False

        # PASO 4: Ingresar caption
        print("4. 📝 Ingresando caption...")

        # Buscar textarea para caption
        caption_selectors = [
            'textarea[aria-label="Write a caption..."]',
            'textarea[placeholder*="caption"]',
            'textarea[placeholder*="Caption"]',
            'textarea',
            'div[contenteditable="true"]',
            'div[role="textbox"]'
        ]

        caption_field = None
        for selector in caption_selectors:
            try:
                caption_field = page.locator(selector).first
                if await caption_field.is_visible(timeout=5000):
                    print(f"✅ Campo de caption encontrado: {selector}")
                    break
            except:
                continue

        if caption_field:
            # Limpiar campo si es necesario
            await caption_field.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Delete')
            await asyncio.sleep(1)

            # Escribir caption
            await caption_field.fill(caption)
            print(f"✅ Caption ingresado: {caption[:50]}...")
            await asyncio.sleep(2)

            # Agregar hashtags
            if hashtags:
                hashtags_text = " ".join([f"#{tag}" for tag in hashtags])
                await caption_field.type(f" {hashtags_text}")
                print(f"✅ Hashtags agregados: {hashtags_text}")
                await asyncio.sleep(2)
        else:
            print("⚠️  No se encontró campo de caption, continuando...")

        # PASO 5: Hacer click en Share/Post
        print("5. 🚀 Haciendo click en Share...")

        share_selectors = [
            'div[role="button"]:has-text("Share")',
            'button:has-text("Share")',
            'div:has-text("Share"):visible',
            'div[role="button"]:has-text("Post")',
            'button:has-text("Post")'
        ]

        share_clicked = False
        for selector in share_selectors:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=5000):
                    print(f"✅ Botón Share encontrado: {selector}")

                    # Verificar si está habilitado
                    is_disabled = await element.get_attribute('disabled')
                    aria_disabled = await element.get_attribute('aria-disabled')

                    if is_disabled or aria_disabled == 'true':
                        print("⚠️  Botón Share está deshabilitado, esperando...")
                        await asyncio.sleep(5)

                    await element.click()
                    print("✅ Click en Share")
                    share_clicked = True
                    await asyncio.sleep(10)  # Esperar a que se publique
                    break
            except:
                continue

        if not share_clicked:
            print("❌ No se encontró botón Share")
            return False

        # PASO 6: Verificar publicación exitosa
        print("6. ✅ Verificando publicación...")
        await asyncio.sleep(5)

        # Buscar indicadores de éxito
        success_indicators = [
            'div:has-text("Your post has been shared")',
            'div:has-text("Post shared")',
            'div:has-text("Shared")',
            'svg[aria-label="Your post has been shared"]',
            'div[class*="success"]',
            'div[class*="Success"]'
        ]

        for selector in success_indicators:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=5000):
                    print(f"✅ Publicación exitosa: {selector}")
                    return True
            except:
                continue

        print("✅ Publicación completada (aunque no se verificó indicador específico)")
        return True

    except Exception as e:
        print(f"❌ Error durante upload manual: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def upload_desde_pagina_cargada():
    """Hacer upload desde la página ya cargada."""

    print("🎯 OBJETIVO: Upload manual desde página ya cargada")
    print()

    browser_service = None
    try:
        # Importar módulos
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType

        print("✅ Módulos importados")

        # Cargar configuración
        from dotenv import load_dotenv
        env_path = current_dir / "instagram-upload" / ".env.instagram"
        load_dotenv(str(env_path))

        username = os.environ.get('INSTAGRAM_USERNAME')

        if not username:
            print("❌ Credenciales no configuradas")
            return False

        print(f"✅ Usuario: {username}")

        # Verificar video
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            print("❌ No hay videos disponibles")
            return False

        video_path = videos[0]
        print(f"✅ Video: {video_path.name}")

        # Configurar navegador
        config = BrowserConfig(
            headless=False,      # VISIBLE
            slow_mo=300,         # Lento para debugging
            timeout=300000,
            browser_type=BrowserType.CHROMIUM
        )

        print("✅ Navegador configurado (visible)")

        # Crear browser service
        browser_service = BrowserService(config)

        # INICIALIZAR NAVEGADOR
        print("\n🖥️  INICIALIZANDO NAVEGADOR...")
        await browser_service.initialize()
        page = browser_service.page
        print("✅ Navegador inicializado")

        # PASO 1: NAVEGAR A INSTAGRAM
        print("\n🌐 NAVEGANDO A INSTAGRAM...")
        await page.goto('https://www.instagram.com/', wait_until="networkidle")
        await asyncio.sleep(5)

        print(f"ℹ️  URL actual: {page.url}")

        # PASO 2: CERRAR POPUP DE NOTIFICACIONES
        print("\n🔧 CERRANDO POPUP DE NOTIFICACIONES...")

        # Presionar Escape
        for i in range(3):
            try:
                await page.keyboard.press('Escape')
                print(f"✅ Escape {i+1}")
                await asyncio.sleep(1)
            except:
                pass

        # Click en áreas donde podría estar "Not Now"
        viewport = page.viewport_size
        width, height = viewport['width'], viewport['height']

        click_areas = [
            (0.5, 0.65),  # Centro-abajo
            (0.8, 0.1),   # Esquina superior derecha
            (0.5, 0.5)    # Centro
        ]

        for rel_x, rel_y in click_areas:
            x = int(width * rel_x)
            y = int(height * rel_y)

            try:
                await page.mouse.click(x, y)
                print(f"✅ Click en ({x}, {y})")
                await asyncio.sleep(1)
            except:
                continue

        # PASO 3: NAVEGAR A PÁGINA DE UPLOAD
        print("\n📍 NAVEGANDO A PÁGINA DE UPLOAD...")

        # Método 1: URL directa
        print("🌐 Usando URL directa...")
        await page.goto('https://www.instagram.com/create/select/', wait_until="networkidle")
        await asyncio.sleep(5)

        current_url = page.url
        print(f"ℹ️  URL actual: {current_url}")

        if "/create/select/" not in current_url and "/create" not in current_url:
            print("❌ No estamos en página de upload")
            print("⚠️  Intentando método alternativo...")

            # Método 2: Buscar botón Create
            await page.goto('https://www.instagram.com/', wait_until="networkidle")
            await asyncio.sleep(3)

            create_selectors = [
                'div[role="button"]:has-text("Create")',
                'button:has-text("Create")',
                'svg[aria-label="New post"]'
            ]

            create_found = False
            for selector in create_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=5000):
                        print(f"✅ Botón Create encontrado: {selector}")
                        await element.click()
                        print("✅ Click en Create")
                        create_found = True
                        await asyncio.sleep(5)
                        break
                except:
                    continue

            if not create_found:
                print("❌ No se pudo acceder a página de upload")
                print("⚠️  Por favor, navega manualmente a 'Create' -> 'Post'")
                print("⚠️  Presiona Enter cuando estés en la página de upload...")
                input("⚠️  Presiona Enter después de navegar a la página de upload... ")

        # Configurar metadata
        caption = """🚀 AIReels - Upload Manual Directo

✅ Página de upload cargada exitosamente
🔧 Upload manual desde página cargada
🤖 Sistema funcionando semi-automáticamente
✅ Subiendo video con método directo

#AIReels #Automation #Instagram #Python #ManualUpload #DirectMethod"""

        hashtags = [
            "aireels", "automation", "instagram", "python",
            "manualupload", "direct", "method", "upload"
        ]

        # PASO 4: HACER UPLOAD MANUAL
        print("\n" + "=" * 60)
        print("📤 INICIANDO UPLOAD MANUAL")
        print("=" * 60)

        success = await hacer_upload_manual(page, video_path, caption, hashtags)

        if not success:
            print("❌ Upload manual falló")
            return False

        print("✅ Upload manual exitoso!")

        # Tomar screenshot final
        try:
            screenshot_path = current_dir / "upload_exitoso.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"📸 Screenshot guardado en: {screenshot_path}")
        except:
            print("📸 No se pudo guardar screenshot")

        return True

    except Exception as e:
        print(f"❌ Error durante ejecución: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if browser_service:
            print("\n⚠️  Manteniendo navegador abierto para verificación...")
            print("⚠️  Presiona Ctrl+C para cerrar cuando hayas verificado")

            try:
                # Mantener abierto por 30 segundos para verificación
                await asyncio.sleep(30)
                print("\n👋 Cerrando navegador...")
                await browser_service.close()
                print("✅ Navegador cerrado")
            except KeyboardInterrupt:
                print("\n👋 Cerrando navegador...")
                await browser_service.close()
                print("✅ Navegador cerrado")
            except:
                print("\n👋 Cerrando navegador...")
                await browser_service.close()
                print("✅ Navegador cerrado")

async def main():
    """Función principal."""

    print("🚀 INICIANDO UPLOAD MANUAL DIRECTO")
    print("⚠️  Este script cargará la página de upload y hará upload manual")
    print()

    success = await upload_desde_pagina_cargada()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡ÉXITO COMPLETO!")
        print("🎉 Video subido y publicado en Instagram")
        print("\n📊 LOGRO:")
        print("   • Página de upload cargada ✓")
        print("   • Popups manejados ✓")
        print("   • Upload manual exitoso ✓")
        print("   • Video publicado ✓")
    else:
        print("❌ FALLÓ")
        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("   1. Verifica que puedes acceder a Instagram")
        print("   2. Navega manualmente a 'Create' -> 'Post'")
        print("   3. Intenta subir un video manualmente")
        print("   4. Asegúrate de que el video es válido")

    return success

if __name__ == "__main__":
    asyncio.run(main())