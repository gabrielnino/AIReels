#!/usr/bin/env python3
"""
UPLOAD CON MANEJO AGRESIVO DE POPUPS
Versión que maneja popups de notificaciones de forma más agresiva
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
print("🚀 UPLOAD CON MANEJO AGRESIVO DE POPUPS")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def cerrar_popup_notificaciones_agresivo(page):
    """Cerrar popup de notificaciones de forma agresiva."""
    print("🔍 BÚSQUEDA AGRESIVA DE POPUP DE NOTIFICACIONES...")

    # Estrategia 1: Buscar botón "Not Now" específicamente
    not_now_selectors = [
        'button:has-text("Not Now")',
        'button:has-text("Not now")',
        'div[role="button"]:has-text("Not Now")',
        'div[role="button"]:has-text("Not now")',
        'span:has-text("Not Now")',
        'span:has-text("Not now")',
        'div:has-text("Not Now")',
        'div:has-text("Not now")'
    ]

    for selector in not_now_selectors:
        try:
            elements = await page.query_selector_all(selector)
            for element in elements[:5]:  # Revisar primeros 5
                try:
                    visible = await element.is_visible()
                    if visible:
                        print(f"⚠️  Elemento encontrado: {selector}")

                        # Obtener posición y hacer click
                        box = await element.bounding_box()
                        if box:
                            x = box['x'] + box['width'] / 2
                            y = box['y'] + box['height'] / 2
                            print(f"📍 Posición: ({x:.0f}, {y:.0f})")

                            await page.mouse.click(x, y)
                            print("✅ Click en posición del botón")
                            await asyncio.sleep(2)
                            return True
                except:
                    continue
        except:
            continue

    # Estrategia 2: Buscar elementos clickeables en la pantalla
    print("🔍 Buscando elementos clickeables en áreas sospechosas...")

    # Áreas comunes donde aparece el popup (centro, arriba)
    areas = [
        (0.5, 0.4),  # Centro-arriba
        (0.5, 0.5),  # Centro
        (0.5, 0.6),  # Centro-abajo
        (0.8, 0.5),  # Derecha-centro
        (0.2, 0.5)   # Izquierda-centro
    ]

    viewport = page.viewport_size
    width, height = viewport['width'], viewport['height']

    for rel_x, rel_y in areas:
        x = int(width * rel_x)
        y = int(height * rel_y)

        try:
            await page.mouse.click(x, y)
            print(f"✅ Click en área ({x}, {y})")
            await asyncio.sleep(1)
        except:
            continue

    # Estrategia 3: Presionar Escape múltiples veces
    print("🔍 Presionando Escape repetidamente...")
    for i in range(5):
        try:
            await page.keyboard.press('Escape')
            print(f"✅ Escape {i+1}")
            await asyncio.sleep(0.5)
        except:
            continue

    # Estrategia 4: Buscar y cerrar modales
    print("🔍 Buscando y cerrando modales...")
    modal_selectors = [
        'div[role="dialog"]',
        'div[role="alertdialog"]',
        'div[aria-modal="true"]',
        'div[data-visualcompletion="ignore"]'
    ]

    for selector in modal_selectors:
        try:
            elements = await page.query_selector_all(selector)
            for i, element in enumerate(elements[:3]):
                try:
                    visible = await element.is_visible()
                    if visible:
                        print(f"⚠️  Modal encontrado: {selector} #{i}")

                        # Intentar encontrar botón de cerrar dentro del modal
                        close_selectors = [
                            'button', 'div[role="button"]', 'svg', 'path'
                        ]

                        for close_sel in close_selectors:
                            try:
                                close_buttons = await element.query_selector_all(close_sel)
                                for btn in close_buttons[:3]:
                                    try:
                                        btn_box = await btn.bounding_box()
                                        if btn_box:
                                            btn_x = btn_box['x'] + btn_box['width'] / 2
                                            btn_y = btn_box['y'] + btn_box['height'] / 2
                                            await page.mouse.click(btn_x, btn_y)
                                            print(f"✅ Click dentro del modal")
                                            await asyncio.sleep(2)
                                            return True
                                    except:
                                        continue
                            except:
                                continue
                except:
                    continue
        except:
            continue

    print("⚠️  No se pudo cerrar popup de manera agresiva")
    return False

async def verificar_y_cerrar_popups(page):
    """Verificar y cerrar popups antes de cualquier acción."""
    print("🔍 VERIFICACIÓN DE POPUPS...")

    # Esperar un momento para que posibles popups aparezcan
    await asyncio.sleep(2)

    # Verificar si hay elementos bloqueando
    print("🔍 Buscando elementos bloqueantes...")

    # Elementos que podrían estar bloqueando
    blocking_selectors = [
        'div[style*="z-index: 999"]',
        'div[style*="z-index: 1000"]',
        'div[style*="position: fixed"]:visible',
        'div[style*="position: absolute"]:visible',
        'div[class*="overlay"]:visible',
        'div[class*="modal"]:visible',
        'div[class*="dialog"]:visible',
        'div[class*="popup"]:visible'
    ]

    for selector in blocking_selectors:
        try:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"⚠️  Elementos bloqueantes encontrados con selector: {selector}")
                print(f"   • Cantidad: {len(elements)}")
        except:
            continue

    # Intentar cerrar popup agresivamente
    closed = await cerrar_popup_notificaciones_agresivo(page)

    if closed:
        print("✅ Popup cerrado agresivamente")
    else:
        print("ℹ️  No se detectó popup bloqueante")

    return closed

async def upload_con_popups_manejados():
    """Upload con manejo agresivo de popups."""

    print("🎯 OBJETIVO: Upload con manejo agresivo de popups")
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
            headless=False,      # VISIBLE
            slow_mo=300,         # Más lento para debugging
            timeout=180000,
            browser_type=BrowserType.CHROMIUM
        )

        print("✅ Navegador configurado (visible, lento)")

        # Crear browser service
        browser_service = BrowserService(config)

        # INICIALIZAR NAVEGADOR
        print("\n🖥️  INICIALIZANDO NAVEGADOR...")
        await browser_service.initialize()
        page = browser_service.page
        print("✅ Navegador inicializado")

        # Navegar a Instagram (ya deberíamos estar logueados)
        print("\n🌐 NAVEGANDO A INSTAGRAM...")
        await page.goto('https://www.instagram.com/')
        await asyncio.sleep(5)

        current_url = page.url
        print(f"ℹ️  URL actual: {current_url}")

        # VERIFICAR Y CERRAR POPUPS INMEDIATAMENTE
        print("\n🔧 MANEJANDO POPUPS INICIALES...")
        popups_cerrados = await verificar_y_cerrar_popups(page)

        if popups_cerrados:
            print("✅ Popups iniciales manejados")
        else:
            print("ℹ️  No se encontraron popups iniciales")

        # Configurar metadata
        caption = """🚀 AIReels - Upload con Manejo de Popups

✅ Navegador único
🔧 Manejo agresivo de popups de notificaciones
🤖 Sistema funcionando autónomamente
✅ Subiendo video de prueba

#AIReels #Automation #Instagram #Python #Popups #Upload #Testing"""

        hashtags = [
            "aireels", "automation", "instagram", "python",
            "popups", "upload", "testing", "notifications"
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

        # PASO 1: UPLOAD
        print("\n" + "=" * 60)
        print("📤 PASO 1: UPLOAD DEL VIDEO")
        print("=" * 60)

        # Verificar y cerrar popups ANTES de upload
        print("\n🔧 VERIFICANDO POPUPS ANTES DE UPLOAD...")
        await verificar_y_cerrar_popups(page)

        print("\n🚀 INICIANDO UPLOAD...")
        upload_result = await video_uploader.upload_video(video_info)

        print(f"   • Status: {upload_result.status}")
        print(f"   • Mensaje: {upload_result.message}")

        if not upload_result.success:
            print("❌ Upload falló")

            # Intentar diagnóstico
            print("\n🔍 DIAGNÓSTICO DEL FALLO...")
            print("   1. Verificando autenticación...")
            await page.goto('https://www.instagram.com/')
            await asyncio.sleep(3)

            current_url = page.url
            print(f"   • URL: {current_url}")

            if "/accounts/login" in current_url:
                print("   ❌ No autenticado - necesitas login")
            else:
                print("   ✅ Autenticado")

            # Verificar popups otra vez
            print("\n   2. Verificando popups...")
            await verificar_y_cerrar_popups(page)

            return False

        print("✅ Upload exitoso")

        # PASO 2: METADATA
        print("\n" + "=" * 60)
        print("🏷️  PASO 2: METADATA")
        print("=" * 60)

        # Verificar y cerrar popups ANTES de metadata
        print("\n🔧 VERIFICANDO POPUPS ANTES DE METADATA...")
        await verificar_y_cerrar_popups(page)

        print("\n📝 INGRESANDO METADATA...")
        metadata_success = await metadata_handler.enter_all_metadata(metadata)

        if not metadata_success:
            print("❌ Metadata falló")
            return False

        print("✅ Metadata ingresada")

        # PASO 3: PUBLICACIÓN
        print("\n" + "=" * 60)
        print("🚀 PASO 3: PUBLICACIÓN")
        print("=" * 60)

        # Verificar y cerrar popups ANTES de publicación
        print("\n🔧 VERIFICANDO POPUPS ANTES DE PUBLICACIÓN...")
        await verificar_y_cerrar_popups(page)

        print("\n📢 PUBLICANDO VIDEO...")
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

    print("🚀 INICIANDO UPLOAD CON MANEJO AGRESIVO DE POPUPS")
    print()

    success = await upload_con_popups_manejados()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡ÉXITO COMPLETO!")
        print("🎉 Video subido y publicado en Instagram")
        print("\n📊 LOGRO:")
        print("   • Navegador único ✓")
        print("   • Manejo agresivo de popups ✓")
        print("   • Upload automático ✓")
        print("   • Metadata automática ✓")
        print("   • Publicación automática ✓")
    else:
        print("❌ FALLÓ")
        print("\n🔧 POSIBLES CAUSAS:")
        print("   1. Problemas de autenticación")
        print("   2. Popup de notificaciones bloqueando")
        print("   3. Selectores cambiados")
        print("   4. Problemas de red")

    return success

if __name__ == "__main__":
    asyncio.run(main())