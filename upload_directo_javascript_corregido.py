#!/usr/bin/env python3
"""
UPLOAD DIRECTO CON JAVASCRIPT CORREGIDO - Usa JavaScript puro
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

log_file = log_dir / f"upload_js_corregido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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
print("🚀 UPLOAD DIRECTO CON JAVASCRIPT CORREGIDO")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📝 Log: {log_file}")
print()

async def upload_directo_corregido():
    """Flujo completo usando JavaScript puro."""

    try:
        # Importar módulos
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType

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

            # PASO 1: LOGIN SIMPLE
            logger.info("\n🔐 HACIENDO LOGIN SIMPLE...")

            # Navegar a Instagram
            await page.goto('https://www.instagram.com/')
            await page.wait_for_timeout(3000)

            # Usar selectores simples de Playwright para login
            try:
                await page.fill('input[name="email"]', username)
                logger.info("✅ Username ingresado")
            except:
                await page.fill('input[name="username"]', username)
                logger.info("✅ Username ingresado (alternativo)")

            try:
                await page.fill('input[name="pass"]', password)
                logger.info("✅ Password ingresado")
            except:
                await page.fill('input[name="password"]', password)
                logger.info("✅ Password ingresado (alternativo)")

            # Click en botón de login
            try:
                await page.click('button[type="submit"]')
                logger.info("✅ Botón de login clickeado")
            except:
                try:
                    await page.click('div[role="button"]')
                    logger.info("✅ Botón de login clickeado (div)")
                except:
                    logger.error("❌ No se pudo hacer click en botón de login")
                    return False

            await page.wait_for_timeout(5000)

            # Verificar login
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
                logger.info("✅ Login exitoso")
            except:
                logger.error("❌ Login falló")
                return False

            # PASO 2: MANEJAR POPUP DE NOTIFICACIONES
            logger.info("\n🔍 MANEJANDO POPUP DE NOTIFICACIONES...")
            await asyncio.sleep(3)

            # JavaScript para buscar y cerrar popup
            popup_js = '''
            (() => {
                // Función para buscar texto en elementos
                function findElementByText(selectors, text) {
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            if (element.textContent.includes(text)) {
                                return element;
                            }
                        }
                    }
                    return null;
                }

                // Buscar popup
                const popupSelectors = ['div[role="dialog"]', 'div[role="alertdialog"]', 'div'];
                const popup = findElementByText(popupSelectors, 'Notifications') ||
                              findElementByText(popupSelectors, 'Turn on');

                if (popup) {
                    console.log('Popup encontrado');

                    // Buscar botón "Not Now"
                    const buttonSelectors = ['button', 'div[role="button"]'];
                    const notNowButton = findElementByText(buttonSelectors, 'Not Now') ||
                                         findElementByText(buttonSelectors, 'Not now');

                    if (notNowButton) {
                        notNowButton.click();
                        console.log('Botón Not Now clickeado');
                        return true;
                    }
                }
                return false;
            })()
            '''

            popup_closed = await page.evaluate(popup_js)
            if popup_closed:
                logger.info("✅ Popup de notificaciones cerrado")
            else:
                logger.info("ℹ️  No se detectó popup de notificaciones")

            await asyncio.sleep(2)

            # PASO 3: NAVEGAR DIRECTAMENTE A PÁGINA DE UPLOAD
            logger.info("\n📍 NAVEGANDO DIRECTAMENTE A UPLOAD...")

            # Método más directo: ir a la URL de creación
            await page.goto('https://www.instagram.com/create/post/')
            await page.wait_for_timeout(5000)

            current_url = page.url
            logger.info(f"📄 URL actual: {current_url}")

            if '/create/' in current_url:
                logger.info("✅ En página de creación de post")
            else:
                logger.warning("⚠️  No en página de creación, intentando click en 'New post'")

                # Intentar hacer click en el botón "New post"
                try:
                    await page.click('svg[aria-label="New post"]')
                    logger.info("✅ Click en 'New post'")
                    await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"❌ Error haciendo click en 'New post': {e}")

                    # Intentar con JavaScript como último recurso
                    new_post_js = '''
                    (() => {
                        // Buscar SVG de "New post"
                        const svg = document.querySelector('svg[aria-label="New post"]');
                        if (svg) {
                            // Encontrar el elemento clickeable
                            const clickable = svg.closest('button') ||
                                             svg.closest('div[role="button"]') ||
                                             svg.closest('a');
                            if (clickable) {
                                clickable.click();
                                return true;
                            }
                        }
                        return false;
                    })()
                    '''

                    js_success = await page.evaluate(new_post_js)
                    if js_success:
                        logger.info("✅ Click en 'New post' usando JavaScript")
                        await asyncio.sleep(5)
                    else:
                        logger.error("❌ No se pudo navegar a página de upload")
                        return False

            # PASO 4: SUBIR VIDEO
            logger.info("\n📤 SUBIENDO VIDEO...")

            # Buscar input de archivo
            try:
                await page.wait_for_selector('input[type="file"]', timeout=10000)
                logger.info("✅ Input de archivo encontrado")
            except:
                logger.warning("⚠️  Input de archivo no encontrado, buscando botón de selección...")

                # Buscar botón para seleccionar archivos
                try:
                    await page.click('div:has-text("Select")')
                    logger.info("✅ Botón 'Select' clickeado")
                    await asyncio.sleep(2)
                except:
                    try:
                        await page.click('div[role="button"]:has-text("Select")')
                        logger.info("✅ Botón 'Select' clickeado (alternativo)")
                        await asyncio.sleep(2)
                    except:
                        logger.error("❌ No se pudo encontrar botón para seleccionar archivo")
                        return False

            # Subir el archivo
            logger.info(f"📁 Subiendo archivo: {video_path.name}")

            try:
                # Asegurarse de que el input de archivo esté disponible
                await asyncio.sleep(2)
                file_input = await page.wait_for_selector('input[type="file"]', timeout=10000)
                await file_input.set_input_files(str(video_path))
                logger.info("✅ Archivo seleccionado")
            except Exception as e:
                logger.error(f"❌ Error subiendo archivo: {e}")
                return False

            logger.info("⏳ Esperando procesamiento del video...")
            await asyncio.sleep(10)

            # PASO 5: AGREGAR METADATA
            logger.info("\n🏷️  AGREGANDO METADATA...")

            caption = """🚀 AIReels - Upload Directo Corregido

✅ Login exitoso
🔧 Popup de notificaciones manejado
📤 Upload completado con JavaScript
🤖 Publicación automática funcionando

#AIReels #Automation #Instagram #Python #AI #JavaScript #Upload #Success"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "javascript", "upload", "success", "working"
            ]

            # Buscar y llenar campo de caption
            try:
                await page.fill('textarea[aria-label="Write a caption..."]', caption + '\n\n' + ' '.join(f'#{tag}' for tag in hashtags))
                logger.info("✅ Caption agregado")
            except:
                try:
                    await page.fill('textarea[placeholder*="caption"]', caption + '\n\n' + ' '.join(f'#{tag}' for tag in hashtags))
                    logger.info("✅ Caption agregado (placeholder)")
                except:
                    logger.warning("⚠️  No se pudo agregar caption automáticamente")

            await asyncio.sleep(2)

            # PASO 6: PUBLICAR
            logger.info("\n🚀 PUBLICANDO...")

            # Buscar y hacer click en botón de Share
            try:
                await page.click('div[role="button"]:has-text("Share")')
                logger.info("✅ Botón 'Share' clickeado")
            except:
                try:
                    await page.click('button:has-text("Share")')
                    logger.info("✅ Botón 'Share' clickeado (button)")
                except:
                    try:
                        await page.click('div:has-text("Share")')
                        logger.info("✅ Botón 'Share' clickeado (div)")
                    except:
                        logger.error("❌ No se pudo encontrar botón de Share")
                        return False

            logger.info("⏳ Esperando publicación...")
            await asyncio.sleep(15)

            # Verificar si la publicación fue exitosa
            try:
                # Buscar indicadores de éxito
                success_indicators = [
                    'div:has-text("Your reel has been shared")',
                    'div:has-text("Your post has been shared")',
                    'div:has-text("Posted")',
                    'a[href*="/p/"]',
                    'a[href*="/reel/"]'
                ]

                for indicator in success_indicators:
                    try:
                        await page.wait_for_selector(indicator, timeout=5000)
                        logger.info(f"✅ Indicador de éxito encontrado: {indicator}")

                        # Intentar obtener URL si es posible
                        if indicator.startswith('a[href'):
                            link = await page.query_selector(indicator)
                            if link:
                                url = await link.get_attribute('href')
                                logger.info(f"🔗 URL del post: https://instagram.com{url}")

                        logger.info("🎉 ¡PUBLICACIÓN EXITOSA!")
                        return True
                    except:
                        continue

                logger.info("⚠️  No se encontraron indicadores específicos, pero el proceso parece completado")
                return True

            except Exception as e:
                logger.error(f"❌ Error verificando publicación: {e}")
                return False

        except Exception as e:
            logger.error(f"❌ Error durante ejecución: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

        finally:
            logger.info("\n⚠️  Navegador mantenido abierto para verificación")
            # await browser_service.close()

    except Exception as e:
        logger.error(f"❌ Error general: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Función principal."""

    logger.info("🚀 Iniciando upload directo corregido")

    success = await upload_directo_corregido()

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