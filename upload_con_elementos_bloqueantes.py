#!/usr/bin/env python3
"""
UPLOAD CON MANEJO ESPECÍFICO DE ELEMENTOS BLOQUEANTES

Este script maneja específicamente elementos que interceptan clicks,
incluyendo el div con tabindex="-1" que bloquea el botón "New post".
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

log_file = log_dir / f"upload_elementos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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
print("🚀 UPLOAD CON MANEJO DE ELEMENTOS BLOQUEANTES")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📝 Log: {log_file}")
print()

async def manejar_elemento_bloqueante_especifico(page):
    """Manejar específicamente el elemento que bloquea clicks en Instagram."""

    logger.info("🔍 Buscando elemento específico que bloquea clicks...")

    # El elemento problemático identificado en logs
    elemento_problematico = 'div[tabindex="-1"].x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj'

    try:
        # Buscar el elemento específico
        elemento = page.locator(elemento_problematico).first
        if await elemento.is_visible(timeout=3000):
            logger.info(f"⚠️  Elemento bloqueante encontrado: {elemento_problematico}")

            # Intentar removerlo del DOM
            try:
                await page.evaluate('''(element) => {
                    element.style.display = 'none';
                    element.style.pointerEvents = 'none';
                }''', elemento)
                logger.info("✅ Elemento bloqueante ocultado")
                await asyncio.sleep(1)
                return True
            except Exception as e:
                logger.error(f"❌ Error ocultando elemento: {e}")

            # Intentar hacer click fuera del área del elemento
            try:
                # Obtener posición del elemento
                box = await elemento.bounding_box()
                if box:
                    # Hacer click en una posición segura (esquina superior izquierda)
                    await page.mouse.click(10, 10)
                    logger.info("✅ Click en posición segura para evitar elemento bloqueante")
                    await asyncio.sleep(1)
                    return True
            except:
                pass

            # Intentar usar JavaScript para hacer click en el botón "New post"
            try:
                await page.evaluate('''() => {
                    const newPostBtn = document.querySelector('svg[aria-label="New post"]');
                    if (newPostBtn) {
                        newPostBtn.closest('button,div[role="button"]')?.click();
                        return true;
                    }
                    return false;
                }''')
                logger.info("✅ Click en 'New post' usando JavaScript")
                await asyncio.sleep(1)
                return True
            except:
                pass

    except Exception as e:
        logger.info(f"ℹ️  Elemento específico no encontrado o error: {e}")

    # Búsqueda más general de elementos bloqueantes
    logger.info("🔍 Buscando elementos bloqueantes generales...")

    selectores_generales = [
        'div[tabindex="-1"]',
        'div[aria-modal="true"]',
        'div[style*="z-index"]',
        'div[style*="position: fixed"]',
        'div[style*="position: absolute"]',
        'div[class*="overlay"]',
        'div[class*="modal"]',
        'div[class*="dialog"]',
        'div[class*="popup"]'
    ]

    for selector in selectores_generales:
        try:
            elementos = await page.query_selector_all(selector)
            for i, elemento in enumerate(elementos[:10]):  # Revisar primeros 10
                try:
                    es_visible = await elemento.is_visible()
                    if es_visible:
                        logger.info(f"⚠️  Elemento potencialmente bloqueante: {selector} #{i}")

                        # Intentar hacer click en él (podría cerrarlo)
                        try:
                            await elemento.click()
                            logger.info(f"✅ Click en elemento bloqueante")
                            await asyncio.sleep(1)
                            return True
                        except:
                            # Intentar removerlo del DOM
                            try:
                                await page.evaluate('(element) => element.style.display = "none"', elemento)
                                logger.info(f"✅ Elemento ocultado")
                                return True
                            except:
                                pass
                except:
                    continue
        except:
            continue

    return False

async def hacer_login_y_navegar(page, username, password):
    """Hacer login y navegar a la página de upload con manejo de elementos."""

    logger.info("🔐 Haciendo login y navegando a Instagram...")

    # Navegar a Instagram
    await page.goto('https://www.instagram.com/')
    await page.wait_for_timeout(3000)

    # Intentar login
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
        return False

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
        return False

    # Esperar login
    await page.wait_for_timeout(5000)

    # Verificar login exitoso
    try:
        await page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
        logger.info("✅ Login exitoso - en página principal")
    except:
        logger.error("❌ No se pudo verificar login exitoso")
        return False

    # Manejar popup de notificaciones
    await asyncio.sleep(3)
    logger.info("🔍 Verificando popup de notificaciones...")

    # Buscar popup de notificaciones
    popup_selectors = [
        'div[role="dialog"]',
        'div[role="alertdialog"]',
        'div[data-testid="notification-popup"]',
        'div:has-text("Turn on Notifications")',
        'div:has-text("Notifications")',
        'div:has-text("Not Now")',
        'div:has-text("Not now")'
    ]

    not_now_buttons = [
        'button:has-text("Not Now")',
        'button:has-text("Not now")',
        'div[role="button"]:has-text("Not Now")',
        'div[role="button"]:has-text("Not now")'
    ]

    for popup_selector in popup_selectors:
        try:
            popup = page.locator(popup_selector).first
            if await popup.is_visible(timeout=3000):
                logger.info(f"⚠️  Popup detectado: {popup_selector}")

                for button_selector in not_now_buttons:
                    try:
                        button = page.locator(button_selector).first
                        if await button.is_visible(timeout=2000):
                            logger.info(f"✅ Botón encontrado: {button_selector}")
                            await button.click()
                            logger.info("✅ Click en 'Not Now'")
                            await asyncio.sleep(2)
                            break
                    except:
                        continue
        except:
            continue

    # Intentar navegar a upload
    logger.info("📍 Navegando a página de upload...")

    # Estrategia 1: Intentar hacer click en "New post" normalmente
    try:
        await page.wait_for_selector('svg[aria-label="New post"]', timeout=10000)
        await page.click('svg[aria-label="New post"]')
        logger.info("✅ Click en 'New post' (estrategia normal)")
        await asyncio.sleep(3)
        return True
    except Exception as e:
        logger.warning(f"⚠️  Estrategia normal falló: {e}")

    # Estrategia 2: Manejar elementos bloqueantes específicos
    logger.info("🔧 Intentando estrategia de elementos bloqueantes...")
    elementos_manejados = await manejar_elemento_bloqueante_especifico(page)

    if elementos_manejados:
        logger.info("✅ Elementos bloqueantes manejados, intentando click de nuevo...")
        await asyncio.sleep(2)

        # Intentar click nuevamente después de manejar elementos
        try:
            await page.click('svg[aria-label="New post"]')
            logger.info("✅ Click en 'New post' después de manejar elementos")
            await asyncio.sleep(3)
            return True
        except Exception as e:
            logger.warning(f"⚠️  Click después de manejar elementos falló: {e}")

    # Estrategia 3: Usar JavaScript para navegar directamente
    logger.info("🔧 Intentando estrategia JavaScript directa...")
    try:
        await page.evaluate('''() => {
            // Intentar varios métodos
            const methods = [
                () => window.location.href = '/create/post/',
                () => window.location.href = '/create/',
                () => {
                    const event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    const newPostBtn = document.querySelector('svg[aria-label="New post"]');
                    if (newPostBtn) newPostBtn.dispatchEvent(event);
                }
            ];

            for (const method of methods) {
                try {
                    method();
                    return true;
                } catch (e) {
                    console.log('Method failed:', e);
                }
            }
            return false;
        }''')

        logger.info("✅ JavaScript ejecutado, esperando navegación...")
        await asyncio.sleep(5)

        # Verificar si estamos en página de upload
        current_url = page.url
        logger.info(f"📄 URL actual: {current_url}")

        if '/create/' in current_url or 'upload' in current_url.lower():
            logger.info("✅ Posiblemente en página de upload")
            return True
        else:
            logger.warning("⚠️  No parece estar en página de upload")
            return False

    except Exception as e:
        logger.error(f"❌ JavaScript strategy failed: {e}")
        return False

    return False

async def upload_con_elementos_bloqueantes():
    """Flujo completo con manejo específico de elementos bloqueantes."""

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

        # Configurar navegador
        config = BrowserConfig(
            headless=False,
            slow_mo=200,
            timeout=180000,
            browser_type=BrowserType.CHROMIUM
        )

        logger.info("✅ Navegador configurado (visible)")

        # Crear browser service
        browser_service = BrowserService(config)

        try:
            # INICIALIZAR NAVEGADOR
            await browser_service.initialize()
            page = browser_service.page
            logger.info("✅ Navegador inicializado")

            # HACER LOGIN Y NAVEGAR A UPLOAD
            navigation_success = await hacer_login_y_navegar(page, username, password)

            if not navigation_success:
                logger.error("❌ No se pudo navegar a página de upload")
                return False

            logger.info("✅ Navegación exitosa a página de upload")

            # Configurar metadata
            caption = """🚀 AIReels - Upload con Manejo de Elementos Bloqueantes

✅ Login exitoso
🔧 Elementos bloqueantes manejados
📍 Navegación a upload exitosa
🤖 Sistema funcionando

#AIReels #Automation #Instagram #Python #AI #Upload #ElementosBloqueantes"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "blockingelements", "debug"
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

            logger.info("✅ Componentes creados")

            # UPLOAD
            logger.info("\n📤 SUBIENDO VIDEO...")
            upload_result = await video_uploader.upload_video(video_info)

            logger.info(f"   • Status: {upload_result.status}")
            logger.info(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                logger.error("❌ Upload falló")
                return False

            logger.info("✅ Upload exitoso")

            # METADATA
            logger.info("\n🏷️  METADATA...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                logger.error("❌ Metadata falló")
                return False

            logger.info("✅ Metadata ingresada")

            # PUBLICACIÓN
            logger.info("\n🚀 PUBLICANDO...")
            publication_result = await publisher.publish_post()

            logger.info(f"   • Status: {publication_result.status}")
            logger.info(f"   • Mensaje: {publication_result.message}")

            if not publication_result.success:
                logger.error("❌ Publicación falló")
                return False

            logger.info("🎉 ¡PUBLICACIÓN EXITOSA!")

            return True

        except Exception as e:
            logger.error(f"❌ Error durante ejecución: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

        finally:
            logger.info("\n⚠️  Navegador mantenido abierto para verificación")

    except Exception as e:
        logger.error(f"❌ Error general: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Función principal."""

    logger.info("🚀 Iniciando upload con manejo de elementos bloqueantes")

    success = await upload_con_elementos_bloqueantes()

    logger.info("\n" + "=" * 80)
    logger.info("🏁 FIN DE EJECUCIÓN")
    logger.info("=" * 80)

    if success:
        logger.info("✅ ¡ÉXITO COMPLETO!")
        logger.info("🎉 Video subido y publicado en Instagram")
    else:
        logger.error("❌ FALLÓ")
        logger.info(f"\n📁 REVISAR LOG: {log_file}")

    return success

if __name__ == "__main__":
    asyncio.run(main())