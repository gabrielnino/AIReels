#!/usr/bin/env python3
"""
UPLOAD CON LOGGING DETALLADO Y CAPTURAS DE HTML

Este script:
1. Incluye logging paso a paso
2. Captura HTML en cada paso crítico
3. Toma screenshots para diagnóstico
4. Maneja popups de notificaciones
"""

import sys
import os
import asyncio
import time
import logging
from pathlib import Path
from datetime import datetime

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))

# Configurar logging
log_dir = current_dir / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

print("=" * 80)
print("🚀 UPLOAD CON LOGGING DETALLADO Y CAPTURAS")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📝 Log: {log_file}")
print()

async def capturar_html(page, nombre_archivo):
    """Capturar HTML de la página actual."""
    try:
        html = await page.content()
        html_file = log_dir / f"{nombre_archivo}_{datetime.now().strftime('%H%M%S')}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"📄 HTML capturado: {html_file.name}")
        return html_file
    except Exception as e:
        logger.error(f"❌ Error capturando HTML: {e}")
        return None

async def capturar_screenshot(page, nombre_archivo):
    """Capturar screenshot de la página actual."""
    try:
        screenshot_dir = log_dir / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)

        screenshot_file = screenshot_dir / f"{nombre_archivo}_{datetime.now().strftime('%H%M%S')}.png"
        await page.screenshot(path=str(screenshot_file), full_page=True)
        logger.info(f"📸 Screenshot capturado: {screenshot_file.name}")
        return screenshot_file
    except Exception as e:
        logger.error(f"❌ Error capturando screenshot: {e}")
        return None

async def hacer_login_directo(page, username, password):
    """Hacer login directamente en la página con logging detallado."""
    logger.info("🔐 Haciendo login directo en Instagram...")

    # Navegar a Instagram
    await page.goto('https://www.instagram.com/')
    await page.wait_for_timeout(3000)

    # Capturar estado inicial
    await capturar_html(page, "01_instagram_home")
    await capturar_screenshot(page, "01_instagram_home")

    # Intentar selectores para campos de login
    username_selectors = [
        'input[name="email"]',
        'input[name="username"]',
        'input[aria-label="Phone number, username, or email"]',
        'input[aria-label*="username"]',
        'input[aria-label*="email"]',
        'input[placeholder*="username"]',
        'input[placeholder*="Username"]',
        'input[placeholder*="email"]',
        'input[placeholder*="Email"]',
        'input[type="text"]:first-of-type'
    ]

    password_selectors = [
        'input[name="pass"]',
        'input[name="password"]',
        'input[aria-label="Password"]',
        'input[aria-label*="password"]',
        'input[placeholder*="password"]',
        'input[placeholder*="Password"]',
        'input[type="password"]',
        'input:nth-of-type(2)'
    ]

    login_button_selectors = [
        'button[type="submit"]',
        'div[role="button"]:has-text("Log in")',
        'button:has-text("Log in")',
        'button:has-text("Log In")'
    ]

    # Intentar username
    username_filled = False
    for selector in username_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            await page.fill(selector, username)
            logger.info(f"✅ Username field: {selector}")
            username_filled = True
            break
        except:
            continue

    if not username_filled:
        logger.error("❌ No se encontró campo de username")
        await capturar_html(page, "02_error_no_username_field")
        await capturar_screenshot(page, "02_error_no_username_field")
        return False

    # Intentar password
    password_filled = False
    for selector in password_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            await page.fill(selector, password)
            logger.info(f"✅ Password field: {selector}")
            password_filled = True
            break
        except:
            continue

    if not password_filled:
        logger.error("❌ No se encontró campo de password")
        await capturar_html(page, "03_error_no_password_field")
        await capturar_screenshot(page, "03_error_no_password_field")
        return False

    # Capturar estado antes de login
    await capturar_html(page, "04_antes_login")
    await capturar_screenshot(page, "04_antes_login")

    # Intentar botón de login
    login_clicked = False
    for selector in login_button_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            await page.click(selector)
            logger.info(f"✅ Login button: {selector}")
            login_clicked = True
            break
        except:
            continue

    if not login_clicked:
        logger.error("❌ No se encontró botón de login")
        await capturar_html(page, "05_error_no_login_button")
        await capturar_screenshot(page, "05_error_no_login_button")
        return False

    # Esperar login
    await page.wait_for_timeout(5000)

    # Capturar estado después de login
    await capturar_html(page, "06_despues_login")
    await capturar_screenshot(page, "06_despues_login")

    # Verificar login exitoso
    try:
        await page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
        logger.info("✅ Login exitoso - en página principal")
        return True
    except:
        logger.error("❌ No se pudo verificar login exitoso")
        # Verificar si hay popup de notificaciones
        popup_manejado = await manejar_popup_notificaciones(page)
        if popup_manejado:
            logger.info("✅ Popup de notificaciones manejado, reintentando verificación...")
            await page.wait_for_timeout(3000)
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
                logger.info("✅ Login exitoso después de manejar popup")
                return True
            except:
                pass

        await capturar_html(page, "07_error_login_fallido")
        await capturar_screenshot(page, "07_error_login_fallido")
        return False

async def manejar_popup_notificaciones(page):
    """Manejar popup de notificaciones de Instagram con logging detallado."""
    logger.info("🔍 Buscando popup de notificaciones...")

    # Selectores para popup de notificaciones "Turn on Notifications"
    popup_selectors = [
        'div[role="dialog"]',
        'div[role="alertdialog"]',
        'div[data-testid="notification-popup"]',
        'div:has-text("Turn on Notifications")',
        'div:has-text("Notifications")',
        'div:has-text("Not Now")',
        'div:has-text("Not now")',
        'div:has-text("Turn on")',
        'div:has-text("Turn On")',
        'div:has-text("notification")',
        'div:has-text("Notification")',
        'div[class*="notification"]',
        'div[class*="Notification"]',
        'div[class*="popup"]',
        'div[class*="Popup"]',
        'div[class*="modal"]',
        'div[class*="Modal"]'
    ]

    # Botones para rechazar notificaciones
    not_now_buttons = [
        'button:has-text("Not Now")',
        'button:has-text("Not now")',
        'button:has-text("Cancel")',
        'button:has-text("cancel")',
        'button:has-text("Close")',
        'button:has-text("close")',
        'button:has-text("Later")',
        'button:has-text("later")',
        'div[role="button"]:has-text("Not Now")',
        'div[role="button"]:has-text("Not now")'
    ]

    try:
        # Buscar popup
        for popup_selector in popup_selectors:
            try:
                popup = page.locator(popup_selector).first
                if await popup.is_visible(timeout=3000):
                    logger.info(f"⚠️  Popup detectado: {popup_selector}")

                    # Capturar popup
                    await capturar_html(page, f"08_popup_{popup_selector[:20]}")
                    await capturar_screenshot(page, f"08_popup_{popup_selector[:20]}")

                    # Buscar y hacer click en "Not Now" o similar
                    for button_selector in not_now_buttons:
                        try:
                            button = page.locator(button_selector).first
                            if await button.is_visible(timeout=2000):
                                logger.info(f"✅ Botón encontrado: {button_selector}")
                                await button.click()
                                logger.info("✅ Click en 'Not Now'")
                                await asyncio.sleep(2)

                                # Capturar después de cerrar popup
                                await capturar_html(page, "09_despues_cerrar_popup")
                                await capturar_screenshot(page, "09_despues_cerrar_popup")
                                return True
                        except:
                            continue

                    # Si no encontró botón específico, intentar cerrar de otras formas
                    logger.warning("⚠️  No se encontró botón específico, intentando alternativas...")

                    # Intentar hacer click fuera del popup
                    try:
                        await page.mouse.click(10, 10)  # Click en esquina
                        logger.info("✅ Click fuera del popup")
                        await asyncio.sleep(2)
                        return True
                    except:
                        pass

                    # Intentar presionar Escape
                    try:
                        await page.keyboard.press('Escape')
                        logger.info("✅ Presionado Escape")
                        await asyncio.sleep(2)
                        return True
                    except:
                        pass

            except:
                continue

        logger.info("ℹ️  No se encontró popup de notificaciones")
        return False

    except Exception as e:
        logger.error(f"❌ Error manejando popup: {e}")
        return False

async def upload_con_logging():
    """Flujo completo con logging detallado."""
    logger.info("🎯 OBJETIVO: Login y upload con logging completo")

    try:
        # Importar módulos
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.upload.video_uploader import VideoUploader, VideoInfo
        from src.upload.metadata_handler import MetadataHandler, VideoMetadata
        from src.upload.publisher import Publisher

        logger.info("✅ Módulos importados")

        # Cargar configuración
        from dotenv import load_dotenv
        env_path = current_dir / "instagram-upload" / ".env.instagram"
        load_dotenv(str(env_path))

        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')

        if not username or not password:
            logger.error("❌ Credenciales no configuradas")
            return False

        logger.info(f"✅ Usuario: {username}")
        logger.info(f"✅ 2FA: DESHABILITADO (configurado en Instagram)")

        # Verificar video
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            logger.error("❌ No hay videos disponibles")
            return False

        video_path = videos[0]
        logger.info(f"✅ Video: {video_path.name}")

        # Configurar navegador
        config = BrowserConfig(
            headless=False,      # VISIBLE
            slow_mo=200,         # Para ver mejor
            timeout=180000,      # 3 minutos
            browser_type=BrowserType.CHROMIUM
        )

        logger.info("✅ Navegador configurado (visible)")

        # Crear browser service
        browser_service = BrowserService(config)

        try:
            # INICIALIZAR NAVEGADOR
            logger.info("\n🖥️  INICIALIZANDO NAVEGADOR ÚNICO...")
            await browser_service.initialize()
            page = browser_service.page
            logger.info("✅ Navegador inicializado")

            # HACER LOGIN DIRECTO
            logger.info("\n🔐 HACIENDO LOGIN DIRECTO...")
            login_success = await hacer_login_directo(page, username, password)

            if not login_success:
                logger.error("❌ Login falló")
                return False

            logger.info("✅ Login exitoso en navegador único")

            # Esperar a que posible popup de notificaciones aparezca después del login
            logger.info("\n⏳ Esperando posibles popups post-login...")
            await asyncio.sleep(5)

            # Verificar popup de notificaciones inmediatamente después del login
            logger.info("🔍 Verificando popup de notificaciones post-login...")
            notificaciones_post_login = await manejar_popup_notificaciones(page)
            if notificaciones_post_login:
                logger.info("✅ Popup de notificaciones cerrado (post-login)")
            else:
                logger.info("ℹ️  No se detectó popup post-login")

            # Configurar metadata
            caption = """🚀 AIReels - Upload Automatizado con Logging

✅ Login sin 2FA exitoso
📝 Logging detallado activado
📸 Screenshots y HTML capturados
🤖 Sistema con diagnóstico completo

#AIReels #Automation #Instagram #Python #AI #Upload #Logging #Diagnostic"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "logging", "diagnostic", "debug"
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

            # Crear componentes de upload
            video_uploader = VideoUploader(browser_service=browser_service)
            metadata_handler = MetadataHandler(browser_service=browser_service)
            publisher = Publisher(browser_service=browser_service)

            logger.info("✅ Componentes creados con mismo browser_service")

            # Resumen antes de upload
            logger.info("\n" + "=" * 60)
            logger.info("🚨 RESUMEN - LISTO PARA UPLOAD")
            logger.info("=" * 60)
            logger.info(f"📋 USANDO MISMO NAVEGADOR PARA:")
            logger.info(f"   1. Login (ya completado)")
            logger.info(f"   2. Upload: {video_path.name}")
            logger.info(f"   3. Metadata")
            logger.info(f"   4. Publicación")

            logger.info("\n⏳ Iniciando upload en 5 segundos...")
            for i in range(5, 0, -1):
                logger.info(f"   {i}...")
                await asyncio.sleep(1)
            logger.info("   🚀 SUBIENDO...")

            # UPLOAD
            logger.info("\n📤 SUBIENDO VIDEO...")
            upload_result = await video_uploader.upload_video(video_info)

            logger.info(f"   • Status: {upload_result.status}")
            logger.info(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                logger.error("❌ Upload falló")
                # Capturar estado después de falla
                await capturar_html(page, "10_error_upload_fallido")
                await capturar_screenshot(page, "10_error_upload_fallido")
                return False

            logger.info("✅ Upload exitoso")
            logger.info(f"   • Duración: {upload_result.duration_seconds:.1f}s")

            # Capturar después de upload
            await capturar_html(page, "11_despues_upload")
            await capturar_screenshot(page, "11_despues_upload")

            # METADATA
            logger.info("\n🏷️  METADATA...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                logger.error("❌ Metadata falló")
                # Capturar estado después de falla
                await capturar_html(page, "12_error_metadata_fallido")
                await capturar_screenshot(page, "12_error_metadata_fallido")
                return False

            logger.info("✅ Metadata ingresada")

            # Capturar después de metadata
            await capturar_html(page, "13_despues_metadata")
            await capturar_screenshot(page, "13_despues_metadata")

            # PUBLICACIÓN
            logger.info("\n🚀 PUBLICANDO...")
            logger.info("⚠️  ¡VIDEO SE PUBLICARÁ EN INSTAGRAM!")

            publication_result = await publisher.publish_post()

            logger.info(f"   • Status: {publication_result.status}")
            logger.info(f"   • Mensaje: {publication_result.message}")

            if not publication_result.success:
                logger.error("❌ Publicación falló")
                # Capturar estado después de falla
                await capturar_html(page, "14_error_publicacion_fallida")
                await capturar_screenshot(page, "14_error_publicacion_fallida")
                return False

            logger.info("🎉 ¡PUBLICACIÓN EXITOSA!")
            if publication_result.post_url:
                logger.info(f"🔗 URL: {publication_result.post_url}")

            # Capturar final exitoso
            await capturar_html(page, "15_exito_final")
            await capturar_screenshot(page, "15_exito_final")

            return True

        except Exception as e:
            logger.error(f"❌ Error durante ejecución: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Capturar error
            await capturar_html(page, "16_error_excepcion")
            await capturar_screenshot(page, "16_error_excepcion")
            return False

        finally:
            # Preguntar antes de cerrar
            logger.info("\n⚠️  Navegador mantenido abierto para verificación")
            # await browser_service.close()

    except ImportError as e:
        logger.error(f"❌ Error importando: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error general: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Función principal."""
    logger.info("🚀 Iniciando upload con logging (login + upload mismo navegador)")
    logger.info("⚠️  2FA DEBE ESTAR DESHABILITADO EN INSTAGRAM")
    logger.info(f"📁 Logs en: {log_dir}")

    success = await upload_con_logging()

    logger.info("\n" + "=" * 80)
    logger.info("🏁 FIN DE EJECUCIÓN")
    logger.info("=" * 80)

    if success:
        logger.info("✅ ¡ÉXITO COMPLETO!")
        logger.info("🎉 Video subido y publicado en Instagram")
        logger.info("\n📊 LOGRO:")
        logger.info("   • Login sin 2FA ✓")
        logger.info("   • Logging detallado ✓")
        logger.info("   • Capturas de HTML y screenshots ✓")
        logger.info("   • Upload automático ✓")
        logger.info("   • Publicación automática ✓")
    else:
        logger.error("❌ FALLÓ")
        logger.info("\n🔧 POSIBLES CAUSAS:")
        logger.info("   1. Credenciales incorrectas")
        logger.info("   2. Instagram aún pide 2FA")
        logger.info("   3. Problemas de red/conexión")
        logger.info("   4. Selectores de Instagram cambiaron")
        logger.info("\n📁 REVISAR:")
        logger.info(f"   • Log completo: {log_file}")
        logger.info(f"   • HTML capturados: logs/*.html")
        logger.info(f"   • Screenshots: logs/screenshots/*.png")

    return success

if __name__ == "__main__":
    asyncio.run(main())