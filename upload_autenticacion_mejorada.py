#!/usr/bin/env python3
"""
UPLOAD CON AUTENTICACIÓN MEJORADA
Versión que soluciona el problema de verificación de autenticación
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
print("🚀 UPLOAD CON AUTENTICACIÓN MEJORADA")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def verificar_autenticacion_mejorada(page):
    """Verificar autenticación con múltiples selectores y lógica mejorada."""
    print("🔍 VERIFICANDO AUTENTICACIÓN MEJORADA...")

    # Esperar a que la página cargue
    await asyncio.sleep(3)

    # Verificar URL actual
    current_url = page.url
    print(f"ℹ️  URL actual: {current_url}")

    # Si estamos en página de login, no estamos autenticados
    if "/accounts/login" in current_url:
        print("❌ No autenticado - en página de login")
        return False

    # Si estamos en instagram.com y NO en login, probablemente estamos autenticados
    if "instagram.com" in current_url and "/accounts/login" not in current_url:
        print("✅ Probablemente autenticado (URL de Instagram no es login)")

        # Verificar selectores de elementos de la página principal
        selectors_autenticacion = [
            'svg[aria-label="Home"]',
            'svg[aria-label="Instagram"]',
            'a[href="/"]',
            'nav',
            'div[role="navigation"]',
            'div[data-testid="primary-nav"]',
            'div:has-text("Home"):visible',
            'div:has-text("Search"):visible',
            'div:has-text("Explore"):visible',
            'div:has-text("Reels"):visible',
            'div:has-text("Create"):visible',
            'button[aria-label="New post"]',
            'button:has-text("Create")'
        ]

        for selector in selectors_autenticacion:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                print(f"✅ Selector de autenticación encontrado: {selector}")
                return True
            except:
                continue

        # Si no encontramos selectores específicos, verificar que NO estamos viendo
        # elementos de login
        selectors_login = [
            'input[name="email"]',
            'input[name="username"]',
            'input[name="pass"]',
            'input[name="password"]',
            'button:has-text("Log in")',
            'button:has-text("Log In")',
            'div:has-text("Log in"):visible',
            'div:has-text("Log In"):visible'
        ]

        login_visible = False
        for selector in selectors_login:
            try:
                element = page.locator(selector).first
                if await element.is_visible(timeout=1000):
                    login_visible = True
                    print(f"⚠️  Elemento de login visible: {selector}")
                    break
            except:
                continue

        if not login_visible:
            print("✅ Confirmado autenticado (no hay elementos de login visibles)")
            return True

    print("❌ No se pudo verificar autenticación")
    return False

async def cerrar_popup_notificaciones_definitivo(page):
    """Cerrar popup de notificaciones de manera definitiva."""
    print("🔧 CERRANDO POPUP DE NOTIFICACIONES DEFINITIVAMENTE...")

    # Estrategia: Buscar cualquier elemento clickeable que pueda cerrar el popup
    for _ in range(3):  # Intentar 3 veces
        # Click en múltiples áreas donde podría estar el botón "Not Now"
        areas = [
            (0.5, 0.6),   # Centro-abajo (donde suele estar "Not Now")
            (0.5, 0.65),  # Un poco más abajo
            (0.5, 0.7),   # Más abajo
            (0.6, 0.6),   # Derecha-abajo
            (0.4, 0.6)    # Izquierda-abajo
        ]

        viewport = page.viewport_size
        width, height = viewport['width'], viewport['height']

        for rel_x, rel_y in areas:
            x = int(width * rel_x)
            y = int(height * rel_y)

            try:
                await page.mouse.click(x, y)
                print(f"✅ Click en posición ({x}, {y})")
                await asyncio.sleep(1)
            except:
                continue

        # Presionar Escape
        try:
            await page.keyboard.press('Escape')
            print("✅ Escape presionado")
            await asyncio.sleep(1)
        except:
            pass

        # Intentar scroll para desbloquear
        try:
            await page.mouse.wheel(0, 100)
            await asyncio.sleep(0.5)
        except:
            pass

    print("✅ Intentos de cerrar popup completados")

async def upload_con_autenticacion_fija():
    """Upload con autenticación mejorada."""

    print("🎯 OBJETIVO: Upload con autenticación verificada correctamente")
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
            slow_mo=500,         # Muy lento para debugging
            timeout=180000,
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

        # PASO 1: NAVEGAR A INSTAGRAM Y VERIFICAR AUTENTICACIÓN
        print("\n🌐 NAVEGANDO A INSTAGRAM...")
        await page.goto('https://www.instagram.com/')
        await asyncio.sleep(5)

        # Verificar autenticación
        autenticado = await verificar_autenticacion_mejorada(page)

        if not autenticado:
            print("❌ No autenticado. Necesitas hacer login manualmente.")
            print("⚠️  Manteniendo navegador abierto para login manual...")

            # Esperar a que el usuario haga login manualmente
            print("⚠️  Por favor, haz login manualmente en el navegador...")
            print("⚠️  Presiona Enter aquí cuando hayas hecho login...")

            input("⚠️  Presiona Enter después de hacer login... ")

            # Verificar autenticación nuevamente
            print("\n🔍 VERIFICANDO AUTENTICACIÓN DESPUÉS DE LOGIN MANUAL...")
            autenticado = await verificar_autenticacion_mejorada(page)

            if not autenticado:
                print("❌ Aún no autenticado después de login manual")
                return False

        print("✅ ¡AUTENTICACIÓN CONFIRMADA!")

        # PASO 2: CERRAR POPUP DE NOTIFICACIONES
        print("\n🔧 CERRANDO POPUP DE NOTIFICACIONES...")
        await cerrar_popup_notificaciones_definitivo(page)

        # Configurar metadata
        caption = """🚀 AIReels - Upload con Autenticación Mejorada

✅ Autenticación verificada correctamente
🔧 Popup de notificaciones manejado
🤖 Sistema funcionando autónomamente
✅ Subiendo video con autenticación garantizada

#AIReels #Automation #Instagram #Python #Authentication #Upload #Testing"""

        hashtags = [
            "aireels", "automation", "instagram", "python",
            "authentication", "upload", "testing", "login"
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

        # Crear VideoUploader personalizado que use nuestra verificación
        print("\n🔧 CREANDO VIDEO UPLOADER PERSONALIZADO...")

        # Monkey patch: Sobrescribir ensure_authenticated en la instancia
        video_uploader = VideoUploader(browser_service=browser_service)

        # Guardar referencia al método original
        original_ensure_auth = video_uploader.ensure_authenticated

        async def patched_ensure_authenticated():
            """Método parcheado para usar nuestra verificación mejorada."""
            print("🔧 USANDO VERIFICACIÓN DE AUTENTICACIÓN PARCHEADA...")

            # Usar nuestra verificación mejorada
            autenticado = await verificar_autenticacion_mejorada(browser_service.page)

            if autenticado:
                video_uploader._is_authenticated = True
                print("✅ Autenticación verificada (parcheado)")
                return True
            else:
                print("❌ Autenticación falló (parcheado)")
                return False

        # Aplicar monkey patch
        video_uploader.ensure_authenticated = patched_ensure_authenticated

        # Crear otros componentes
        metadata_handler = MetadataHandler(browser_service=browser_service)
        publisher = Publisher(browser_service=browser_service)

        print("✅ Componentes creados (VideoUploader parcheado)")

        # PASO 3: UPLOAD
        print("\n" + "=" * 60)
        print("📤 INICIANDO UPLOAD")
        print("=" * 60)

        print("\n🚀 SUBIENDO VIDEO...")
        upload_result = await video_uploader.upload_video(video_info)

        print(f"   • Status: {upload_result.status}")
        print(f"   • Mensaje: {upload_result.message}")

        if not upload_result.success:
            print("❌ Upload falló")
            return False

        print("✅ Upload exitoso")

        # PASO 4: METADATA
        print("\n🏷️  METADATA...")
        metadata_success = await metadata_handler.enter_all_metadata(metadata)

        if not metadata_success:
            print("❌ Metadata falló")
            return False

        print("✅ Metadata ingresada")

        # PASO 5: PUBLICACIÓN
        print("\n🚀 PUBLICANDO...")
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

    print("🚀 INICIANDO UPLOAD CON AUTENTICACIÓN MEJORADA")
    print()

    success = await upload_con_autenticacion_fija()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡ÉXITO COMPLETO!")
        print("🎉 Video subido y publicado en Instagram")
        print("\n📊 LOGRO:")
        print("   • Autenticación verificada ✓")
        print("   • VideoUploader parcheado ✓")
        print("   • Popups manejados ✓")
        print("   • Upload automático ✓")
        print("   • Publicación automática ✓")
    else:
        print("❌ FALLÓ")
        print("\n🔧 RECOMENDACIONES:")
        print("   1. Verifica que estás logueado en Instagram")
        print("   2. Cierra manualmente cualquier popup")
        print("   3. Asegúrate de que 2FA está deshabilitado")
        print("   4. Intenta hacer login manualmente primero")

    return success

if __name__ == "__main__":
    asyncio.run(main())