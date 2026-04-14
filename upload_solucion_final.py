#!/usr/bin/env python3
"""
SOLUCIÓN FINAL PARA UPLOAD A INSTAGRAM
- Manejo completo de popups de notificaciones
- Navegación directa a upload
- Debugging extensivo
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
print("🚀 SOLUCIÓN FINAL - UPLOAD A INSTAGRAM")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def navegar_directamente_a_upload(page):
    """Navegar directamente a la página de upload de Instagram."""
    print("📍 NAVEGANDO DIRECTAMENTE A PÁGINA DE UPLOAD...")

    # Intentar diferentes URLs de upload
    upload_urls = [
        "https://www.instagram.com/create/select/",
        "https://www.instagram.com/create",
        "https://www.instagram.com/create/",
        "https://www.instagram.com/"
    ]

    for url in upload_urls:
        print(f"🌐 Intentando: {url}")
        try:
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(3)

            # Verificar si estamos en página de upload
            current_url = page.url
            print(f"ℹ️  URL actual: {current_url}")

            # Buscar botón de crear post
            create_selectors = [
                'div[role="button"]:has-text("Create")',
                'button:has-text("Create")',
                'svg[aria-label="New post"]',
                'svg[aria-label="Create"]',
                'div[aria-label="New post"]',
                'div[aria-label="Create"]',
                'div:has-text("Create"):visible',
                'div:has-text("Create post"):visible'
            ]

            for selector in create_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=3000):
                        print(f"✅ Botón Create encontrado: {selector}")
                        await element.click()
                        print("✅ Click en botón Create")
                        await asyncio.sleep(3)
                        return True
                except:
                    continue

            # Si estamos en la página de selección de archivos, éxito
            if "/create/select/" in current_url or "/create" in current_url:
                print("✅ Ya en página de upload")
                return True

        except Exception as e:
            print(f"⚠️  Error navegando a {url}: {e}")

    print("❌ No se pudo navegar a página de upload")
    return False

async def cerrar_todos_los_popups(page):
    """Cerrar todos los popups de manera exhaustiva."""
    print("🔧 CERRANDO TODOS LOS POPUPS...")

    # Estrategia 1: Presionar Escape múltiples veces
    print("🔧 Presionando Escape...")
    for i in range(5):
        try:
            await page.keyboard.press('Escape')
            print(f"✅ Escape {i+1}")
            await asyncio.sleep(0.5)
        except:
            pass

    # Estrategia 2: Click en áreas específicas donde podría estar "Not Now"
    print("🔧 Click en áreas de Not Now...")
    viewport = page.viewport_size
    width, height = viewport['width'], viewport['height']

    # Áreas donde suele aparecer el botón "Not Now"
    not_now_areas = [
        (0.5, 0.65),   # Centro-abajo (más común)
        (0.5, 0.7),    # Más abajo
        (0.6, 0.65),   # Derecha-abajo
        (0.4, 0.65),   # Izquierda-abajo
        (0.5, 0.6),    # Centro
        (0.8, 0.1),    # Esquina superior derecha (botón X)
        (0.9, 0.1)     # Esquina superior derecha extrema
    ]

    for rel_x, rel_y in not_now_areas:
        x = int(width * rel_x)
        y = int(height * rel_y)

        try:
            await page.mouse.click(x, y)
            print(f"✅ Click en ({x}, {y})")
            await asyncio.sleep(0.5)
        except:
            continue

    # Estrategia 3: Buscar y hacer click en cualquier botón que diga "Not Now"
    print("🔧 Buscando botones Not Now...")
    not_now_texts = ["Not Now", "Not now", "Cancel", "Later", "Close", "X", "×"]

    for text in not_now_texts:
        selectors = [
            f'button:has-text("{text}")',
            f'div[role="button"]:has-text("{text}")',
            f'div:has-text("{text}"):visible',
            f'span:has-text("{text}"):visible',
            f'a:has-text("{text}"):visible'
        ]

        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements[:3]:
                    try:
                        visible = await element.is_visible()
                        if visible:
                            print(f"⚠️  Botón encontrado: {text}")
                            await element.click()
                            print(f"✅ Click en botón: {text}")
                            await asyncio.sleep(2)
                            return True
                    except:
                        continue
            except:
                continue

    # Estrategia 4: Buscar modales y cerrarlos
    print("🔧 Buscando y cerrando modales...")
    modal_selectors = [
        'div[role="dialog"]',
        'div[role="alertdialog"]',
        'div[aria-modal="true"]',
        'div[data-visualcompletion="ignore"]',
        'div[style*="z-index: 999"]',
        'div[style*="z-index: 1000"]',
        'div[style*="position: fixed"]',
        'div[class*="modal"]',
        'div[class*="Modal"]',
        'div[class*="popup"]',
        'div[class*="Popup"]'
    ]

    for selector in modal_selectors:
        try:
            elements = await page.query_selector_all(selector)
            for i, element in enumerate(elements[:3]):
                try:
                    visible = await element.is_visible()
                    if visible:
                        print(f"⚠️  Modal encontrado: {selector} #{i}")

                        # Intentar encontrar botón de cerrar
                        close_selectors = ['button', 'div[role="button"]', 'svg', 'path', '[aria-label="Close"]']

                        for close_sel in close_selectors:
                            try:
                                close_elements = await element.query_selector_all(close_sel)
                                for btn in close_elements[:3]:
                                    try:
                                        await btn.click()
                                        print(f"✅ Click en botón dentro del modal")
                                        await asyncio.sleep(2)
                                        return True
                                    except:
                                        continue
                            except:
                                continue

                        # Si no encuentra botón, hacer click en el modal
                        try:
                            box = await element.bounding_box()
                            if box:
                                x = box['x'] + box['width'] / 2
                                y = box['y'] + box['height'] / 2
                                await page.mouse.click(x, y)
                                print(f"✅ Click en centro del modal")
                                await asyncio.sleep(2)
                        except:
                            pass
                except:
                    continue
        except:
            continue

    print("✅ Todos los popups manejados (o no había)")
    return False

async def upload_solucion_final():
    """Solución final para upload con manejo completo de popups."""

    print("🎯 OBJETIVO: Upload exitoso con manejo completo de problemas")
    print()

    browser_service = None
    try:
        # Importar módulos
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.upload.video_uploader import VideoUploader, VideoInfo
        from src.upload.metadata_handler import MetadataHandler, VideoMetadata
        from src.upload.publisher import Publisher

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
            headless=False,      # VISIBLE para debugging
            slow_mo=500,         # Muy lento para ver qué pasa
            timeout=300000,      # 5 minutos
            browser_type=BrowserType.CHROMIUM
        )

        print("✅ Navegador configurado (visible, muy lento)")

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

        # PASO 2: CERRAR TODOS LOS POPUPS
        print("\n🔧 PASO CRÍTICO: CERRANDO TODOS LOS POPUPS...")
        await cerrar_todos_los_popups(page)
        await asyncio.sleep(3)

        # PASO 3: NAVEGAR DIRECTAMENTE A UPLOAD
        print("\n📍 PASO CRÍTICO: NAVEGANDO A UPLOAD...")
        upload_success = await navegar_directamente_a_upload(page)

        if not upload_success:
            print("❌ No se pudo navegar a upload")
            print("⚠️  Intentando método alternativo...")

            # Método alternativo: Ir a Instagram y buscar botón Create
            await page.goto('https://www.instagram.com/', wait_until="networkidle")
            await asyncio.sleep(3)

            # Cerrar popups nuevamente
            await cerrar_todos_los_popups(page)
            await asyncio.sleep(2)

            # Buscar botón Create específicamente
            print("🔍 Buscando botón Create manualmente...")
            create_selectors = [
                'div[role="button"]:has-text("Create")',
                'button:has-text("Create")',
                'svg[aria-label="New post"]',
                'div[aria-label="New post"]'
            ]

            for selector in create_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=5000):
                        print(f"✅ Botón Create encontrado: {selector}")
                        await element.click()
                        print("✅ Click en botón Create")
                        await asyncio.sleep(3)
                        upload_success = True
                        break
                except:
                    continue

            if not upload_success:
                print("❌ No se pudo encontrar botón Create")
                print("⚠️  Intentando con URL directa...")

                # Último intento: URL directa
                await page.goto('https://www.instagram.com/create/select/', wait_until="networkidle")
                await asyncio.sleep(3)

                # Verificar si estamos en página de upload
                current_url = page.url
                if "/create/select/" in current_url or "/create" in current_url:
                    print("✅ En página de upload (URL directa)")
                    upload_success = True

        if not upload_success:
            print("❌ No se pudo acceder a página de upload después de múltiples intentos")
            print("⚠️  Manteniendo navegador abierto para diagnóstico...")
            print("⚠️  Por favor, navega manualmente a la página de upload y presiona Enter...")
            input("⚠️  Presiona Enter después de navegar a la página de upload... ")

        # Configurar metadata
        caption = """🚀 AIReels - Solución Final para Upload

✅ Popups manejados completamente
🔧 Navegación directa a upload
🤖 Sistema funcionando autónomamente
✅ Subiendo video con solución final

#AIReels #Automation #Instagram #Python #Upload #FinalSolution #PopupsHandled"""

        hashtags = [
            "aireels", "automation", "instagram", "python",
            "upload", "finalsolution", "popups", "notification"
        ]

        # Preparar video info y metadata
        video_info = VideoInfo(
            path=str(video_path),
            caption=caption,
            hashtags=hashtags,
            location="AIReels Lab"
        )

        metadata = VideoMetadata(
            caption=caption,
            hashtags=hashtags,
            location="AIReels Lab"
        )

        # Crear componentes
        video_uploader = VideoUploader(browser_service=browser_service)
        metadata_handler = MetadataHandler(browser_service=browser_service)
        publisher = Publisher(browser_service=browser_service)

        print("✅ Componentes creados")

        # PASO 4: UPLOAD
        print("\n" + "=" * 60)
        print("📤 INICIANDO UPLOAD DEL VIDEO")
        print("=" * 60)

        print("\n🚀 EJECUTANDO UPLOAD...")
        upload_result = await video_uploader.upload_video(video_info)

        print(f"   • Status: {upload_result.status}")
        print(f"   • Mensaje: {upload_result.message}")

        if not upload_result.success:
            print("❌ Upload falló")

            # Diagnóstico adicional
            print("\n🔍 DIAGNÓSTICO DETALLADO:")
            print(f"   1. URL actual: {page.url}")
            print(f"   2. Título de página: {await page.title()}")

            # Tomar screenshot para diagnóstico
            try:
                screenshot_path = current_dir / "upload_error.png"
                await page.screenshot(path=str(screenshot_path))
                print(f"   3. Screenshot guardado en: {screenshot_path}")
            except:
                print("   3. No se pudo tomar screenshot")

            return False

        print("✅ Upload exitoso")

        # PASO 5: METADATA
        print("\n🏷️  INGRESANDO METADATA...")
        metadata_success = await metadata_handler.enter_all_metadata(metadata)

        if not metadata_success:
            print("❌ Metadata falló")
            return False

        print("✅ Metadata ingresada")

        # PASO 6: PUBLICACIÓN
        print("\n🚀 PUBLICANDO VIDEO...")
        print("⚠️  ¡EL VIDEO SE PUBLICARÁ EN INSTAGRAM!")

        publication_result = await publisher.publish_post()

        print(f"   • Status: {publication_result.status}")
        print(f"   • Mensaje: {publication_result.message}")

        if not publication_result.success:
            print("❌ Publicación falló")
            return False

        print("🎉 ¡PUBLICACIÓN EXITOSA!")
        if publication_result.post_url:
            print(f"🔗 URL: {publication_result.post_url}")

        return True

    except Exception as e:
        print(f"❌ Error durante ejecución: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if browser_service:
            print("\n⚠️  Cerrando navegador...")
            await browser_service.close()
            print("✅ Navegador cerrado")

async def main():
    """Función principal."""

    print("🚀 EJECUTANDO SOLUCIÓN FINAL PARA UPLOAD")
    print("⚠️  Este script manejará popups y navegará directamente a upload")
    print()

    success = await upload_solucion_final()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡ÉXITO COMPLETO!")
        print("🎉 Video subido y publicado en Instagram")
        print("\n📊 LOGRO:")
        print("   • Popups manejados completamente ✓")
        print("   • Navegación a upload exitosa ✓")
        print("   • Upload automático ✓")
        print("   • Metadata automática ✓")
        print("   • Publicación automática ✓")
    else:
        print("❌ FALLÓ")
        print("\n🔧 ACCIONES RECOMENDADAS:")
        print("   1. Verifica que puedes acceder manualmente a Instagram")
        print("   2. Cierra manualmente cualquier popup de notificaciones")
        print("   3. Navega manualmente a 'Create' -> 'Post'")
        print("   4. Asegúrate de que 2FA está deshabilitado")
        print("   5. Intenta el proceso manualmente primero")

    return success

if __name__ == "__main__":
    asyncio.run(main())