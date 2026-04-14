#!/usr/bin/env python3
"""
UPLOAD FINAL COMPLETO - Combina lo mejor de todos los scripts

✅ Manejo de popup de notificaciones
✅ Login simple y directo
✅ Navegación a upload con manejo de elementos bloqueantes
✅ Subida de video
✅ Metadata y publicación
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

log_file = log_dir / f"upload_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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
print("🚀 UPLOAD FINAL COMPLETO")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📝 Log: {log_file}")
print()

async def cerrar_elemento_bloqueante(page):
    """Cerrar específicamente el elemento que bloquea clicks."""

    logger.info("🔍 Buscando elemento bloqueante específico...")

    # El elemento que identificamos en logs anteriores
    elemento_bloqueante = 'div[tabindex="-1"].x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj'

    try:
        elemento = page.locator(elemento_bloqueante).first
        if await elemento.is_visible(timeout=2000):
            logger.info(f"⚠️  Elemento bloqueante encontrado: {elemento_bloqueante}")

            # Intentar varias estrategias
            estrategias = [
                # 1. Hacer click fuera del elemento
                lambda: page.mouse.click(10, 10),
                # 2. Presionar Escape
                lambda: page.keyboard.press('Escape'),
                # 3. Ocultar elemento con JavaScript
                lambda: page.evaluate('''(element) => {
                    element.style.display = 'none';
                    element.style.pointerEvents = 'none';
                }''', elemento)
            ]

            for i, estrategia in enumerate(estrategias):
                try:
                    await estrategia()
                    logger.info(f"✅ Estrategia {i+1} exitosa")
                    await asyncio.sleep(1)
                    return True
                except:
                    continue

    except:
        pass

    return False

async def upload_final_completo():
    """Flujo completo final."""

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

        # Verificar video
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            logger.error("❌ No hay videos disponibles")
            return False

        video_path = videos[0]
        logger.info(f"✅ Video: {video_path.name}")

        # Configurar navegador - MÁS LENTO para mejor visibilidad
        config = BrowserConfig(
            headless=False,
            slow_mo=500,  # Más lento para ver mejor
            timeout=240000,  # 4 minutos
            browser_type=BrowserType.CHROMIUM
        )

        logger.info("✅ Navegador configurado (visible, lento)")

        # Crear browser service
        browser_service = BrowserService(config)

        try:
            # INICIALIZAR NAVEGADOR
            await browser_service.initialize()
            page = browser_service.page
            logger.info("✅ Navegador inicializado")

            # PASO 1: LOGIN DIRECTO Y LENTO
            logger.info("\n🔐 LOGIN DIRECTO (PASO A PASO)...")

            # Navegar a Instagram
            await page.goto('https://www.instagram.com/')
            await asyncio.sleep(3)
            logger.info("✅ Navegado a Instagram")

            # Llenar username
            try:
                await page.fill('input[name="email"]', username)
                logger.info("✅ Username ingresado")
                await asyncio.sleep(1)
            except:
                try:
                    await page.fill('input[name="username"]', username)
                    logger.info("✅ Username ingresado (alternativo)")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"❌ Error con username: {e}")
                    return False

            # Llenar password
            try:
                await page.fill('input[name="pass"]', password)
                logger.info("✅ Password ingresado")
                await asyncio.sleep(1)
            except:
                try:
                    await page.fill('input[name="password"]', password)
                    logger.info("✅ Password ingresado (alternativo)")
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"❌ Error con password: {e}")
                    return False

            # Click en botón de login
            try:
                await page.click('button[type="submit"]')
                logger.info("✅ Botón de login clickeado")
            except:
                try:
                    await page.click('div[role="button"]')
                    logger.info("✅ Botón de login clickeado (div role=button)")
                except:
                    try:
                        # Intentar cualquier botón visible
                        await page.evaluate('''() => {
                            const buttons = document.querySelectorAll('button, div[role="button"]');
                            for (const btn of buttons) {
                                if (btn.textContent.includes('Log') || btn.textContent.includes('LOG')) {
                                    btn.click();
                                    return true;
                                }
                            }
                            return false;
                        }''')
                        logger.info("✅ Botón de login clickeado (JavaScript)")
                    except Exception as e:
                        logger.error(f"❌ Error haciendo click en botón de login: {e}")
                        return False

            logger.info("⏳ Esperando login...")
            await asyncio.sleep(8)

            # Verificar login
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=15000)
                logger.info("✅ Login exitoso - En página principal")
            except Exception as e:
                logger.error(f"❌ Login falló: {e}")
                return False

            # PASO 2: MANEJAR POPUP DE NOTIFICACIONES
            logger.info("\n🔍 MANEJANDO POPUP DE NOTIFICACIONES...")
            await asyncio.sleep(3)

            # Buscar popup
            popup_selectors = [
                'div:has-text("Turn on Notifications")',
                'div:has-text("Notifications")',
                'div:has-text("Not Now")',
                'div[role="dialog"]'
            ]

            for selector in popup_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        logger.info(f"⚠️  Popup encontrado: {selector}")

                        # Buscar botón "Not Now"
                        button_selectors = [
                            'button:has-text("Not Now")',
                            'button:has-text("Not now")',
                            'div[role="button"]:has-text("Not Now")',
                            'div[role="button"]:has-text("Not now")'
                        ]

                        for btn_selector in button_selectors:
                            try:
                                button = page.locator(btn_selector).first
                                if await button.is_visible(timeout=1000):
                                    logger.info(f"✅ Botón encontrado: {btn_selector}")
                                    await button.click()
                                    logger.info("✅ Click en 'Not Now'")
                                    await asyncio.sleep(2)
                                    break
                            except:
                                continue
                        break
                except:
                    continue

            logger.info("✅ Popup de notificaciones manejado")

            # PASO 3: NAVEGAR A UPLOAD CON MANEJO DE ELEMENTOS BLOQUEANTES
            logger.info("\n📍 NAVEGANDO A UPLOAD...")
            await asyncio.sleep(2)

            # Intentar varias veces con manejo de elementos bloqueantes
            for intento in range(3):
                logger.info(f"🔄 Intento {intento + 1}/3 de navegar a upload...")

                try:
                    # Primero intentar manejar elemento bloqueante
                    if intento > 0:
                        await cerrar_elemento_bloqueante(page)
                        await asyncio.sleep(1)

                    # Intentar hacer click en "New post"
                    await page.click('svg[aria-label="New post"]')
                    logger.info("✅ Click en 'New post'")
                    await asyncio.sleep(5)

                    # Verificar si estamos en página de upload
                    current_url = page.url
                    if '/create/' in current_url:
                        logger.info(f"✅ En página de upload: {current_url}")
                        break
                    else:
                        logger.warning(f"⚠️  No en página de upload: {current_url}")

                except Exception as e:
                    logger.warning(f"⚠️  Error en intento {intento + 1}: {e}")
                    await asyncio.sleep(2)

                    if intento == 2:  # Último intento
                        logger.error("❌ No se pudo navegar a upload después de 3 intentos")

                        # Último recurso: navegar directamente
                        logger.info("🔄 Intentando navegación directa...")
                        await page.goto('https://www.instagram.com/create/post/')
                        await asyncio.sleep(5)

                        current_url = page.url
                        if '/create/' in current_url:
                            logger.info(f"✅ En página de upload (directa): {current_url}")
                        else:
                            logger.error("❌ No se pudo navegar a página de upload")
                            return False

            # PASO 4: CONFIGURAR Y USAR LOS MÓDULOS DE UPLOAD
            logger.info("\n🔧 CONFIGURANDO MÓDULOS DE UPLOAD...")

            caption = """🚀 AIReels - Upload Final Completo

✅ Login exitoso sin 2FA
🔧 Popup de notificaciones manejado
📍 Navegación a upload exitosa
📤 Video subido automáticamente
🏷️ Metadata configurada
🚀 Publicado en Instagram

#AIReels #Automation #Instagram #Python #AI #Upload #Complete #Success"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "complete", "success", "final"
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

            logger.info("✅ Componentes de upload creados")

            # PASO 5: SUBIR VIDEO
            logger.info("\n📤 SUBIENDO VIDEO...")
            logger.info(f"📁 Archivo: {video_path.name}")

            upload_result = await video_uploader.upload_video(video_info)

            logger.info(f"   • Status: {upload_result.status}")
            logger.info(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                logger.error("❌ Upload falló")
                return False

            logger.info("✅ Upload exitoso")
            await asyncio.sleep(3)

            # PASO 6: METADATA
            logger.info("\n🏷️  METADATA...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                logger.error("❌ Metadata falló")
                return False

            logger.info("✅ Metadata ingresada")
            await asyncio.sleep(2)

            # PASO 7: PUBLICAR
            logger.info("\n🚀 PUBLICANDO...")
            logger.info("⚠️  ¡ESTE VIDEO SE PUBLICARÁ EN INSTAGRAM!")

            # Esperar confirmación visual
            for i in range(5, 0, -1):
                logger.info(f"   Publicando en {i}...")
                await asyncio.sleep(1)

            publication_result = await publisher.publish_post()

            logger.info(f"   • Status: {publication_result.status}")
            logger.info(f"   • Mensaje: {publication_result.message}")

            if not publication_result.success:
                logger.error("❌ Publicación falló")
                return False

            logger.info("🎉 ¡PUBLICACIÓN EXITOSA!")

            if publication_result.post_url:
                logger.info(f"🔗 URL del post: {publication_result.post_url}")

            # Esperar para ver resultado
            logger.info("⏳ Esperando para ver post publicado...")
            await asyncio.sleep(10)

            return True

        except Exception as e:
            logger.error(f"❌ Error durante ejecución: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

        finally:
            logger.info("\n⚠️  Navegador mantenido abierto para verificación")
            logger.info("   Puedes cerrar el navegador manualmente cuando hayas verificado")

    except Exception as e:
        logger.error(f"❌ Error general: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Función principal."""

    logger.info("🚀 INICIANDO UPLOAD FINAL COMPLETO")
    logger.info("⚠️  2FA DEBE ESTAR DESHABILITADO EN INSTAGRAM")
    logger.info("📁 Los logs detallados se guardan en: logs/")
    logger.info("")

    success = await upload_final_completo()

    logger.info("\n" + "=" * 80)
    logger.info("🏁 FIN DE EJECUCIÓN")
    logger.info("=" * 80)

    if success:
        logger.info("✅ ¡ÉXITO COMPLETO!")
        logger.info("🎉 Video subido y publicado en Instagram")
        logger.info("\n📊 RESUMEN DE LOGROS:")
        logger.info("   1. ✅ Login exitoso sin 2FA")
        logger.info("   2. ✅ Popup de notificaciones manejado")
        logger.info("   3. ✅ Navegación a upload exitosa")
        logger.info("   4. ✅ Video subido")
        logger.info("   5. ✅ Metadata configurada")
        logger.info("   6. ✅ Publicación exitosa")
    else:
        logger.error("❌ FALLÓ")
        logger.info("\n🔧 POSIBLES SOLUCIONES:")
        logger.info("   1. Verificar credenciales en .env.instagram")
        logger.info("   2. Asegurar que 2FA está deshabilitado en Instagram")
        logger.info("   3. Verificar conexión a internet")
        logger.info("   4. Revisar logs detallados para diagnóstico")
        logger.info(f"\n📁 LOG DETALLADO: {log_file}")

    return success

if __name__ == "__main__":
    asyncio.run(main())