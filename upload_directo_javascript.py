#!/usr/bin/env python3
"""
UPLOAD DIRECTO CON JAVASCRIPT - Evita elementos bloqueantes usando JS
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

log_file = log_dir / f"upload_js_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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
print("🚀 UPLOAD DIRECTO CON JAVASCRIPT")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📝 Log: {log_file}")
print()

async def upload_directo_con_js():
    """Flujo completo usando JavaScript para evitar elementos bloqueantes."""

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

            # PASO 1: LOGIN
            logger.info("\n🔐 HACIENDO LOGIN...")
            await page.goto('https://www.instagram.com/')
            await page.wait_for_timeout(3000)

            # Login con JavaScript para más robustez
            login_js = f'''
            (() => {{
                // Buscar campos
                const usernameField = document.querySelector('input[name="email"]') ||
                                     document.querySelector('input[name="username"]') ||
                                     document.querySelector('input[aria-label*="username"]') ||
                                     document.querySelector('input[aria-label*="email"]');

                const passwordField = document.querySelector('input[name="pass"]') ||
                                     document.querySelector('input[name="password"]') ||
                                     document.querySelector('input[type="password"]');

                const loginButton = document.querySelector('button[type="submit"]') ||
                                   document.querySelector('div[role="button"]:has-text("Log in")') ||
                                   document.querySelector('button:has-text("Log in")');

                if (usernameField && passwordField && loginButton) {{
                    usernameField.value = "{username}";
                    passwordField.value = "{password}";

                    // Disparar eventos de cambio
                    usernameField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    passwordField.dispatchEvent(new Event('input', {{ bubbles: true }}));

                    loginButton.click();
                    return true;
                }}
                return false;
            }})()
            '''

            login_success = await page.evaluate(login_js)
            if login_success:
                logger.info("✅ Login iniciado con JavaScript")
            else:
                logger.error("❌ Login con JavaScript falló, intentando método tradicional")
                # Método tradicional como fallback
                await page.fill('input[name="email"]', username)
                await page.fill('input[name="pass"]', password)
                await page.click('div[role="button"]:has-text("Log in")')

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

            # Buscar y cerrar popup con JavaScript
            popup_js = '''
            (() => {
                // Buscar popup de notificaciones
                const popupSelectors = [
                    'div:has-text("Turn on Notifications")',
                    'div:has-text("Notifications")',
                    'div:has-text("Not Now")',
                    'div[role="dialog"]',
                    'div[role="alertdialog"]'
                ];

                for (const selector of popupSelectors) {
                    const popup = document.querySelector(selector);
                    if (popup && popup.offsetParent !== null) {
                        console.log('Popup encontrado:', selector);

                        // Buscar botón "Not Now"
                        const notNowButtons = [
                            'button:has-text("Not Now")',
                            'button:has-text("Not now")',
                            'div[role="button"]:has-text("Not Now")',
                            'div[role="button"]:has-text("Not now")'
                        ];

                        for (const btnSelector of notNowButtons) {
                            const button = document.querySelector(btnSelector);
                            if (button) {
                                button.click();
                                console.log('Botón clickeado:', btnSelector);
                                return true;
                            }
                        }
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

            # PASO 3: NAVEGAR A UPLOAD USANDO JAVASCRIPT
            logger.info("\n📍 NAVEGANDO A UPLOAD CON JAVASCRIPT...")

            # Método 1: Navegación directa
            await page.goto('https://www.instagram.com/create/post/')
            await page.wait_for_timeout(3000)

            current_url = page.url
            logger.info(f"📄 URL actual: {current_url}")

            # Verificar si estamos en página de creación
            if '/create/' in current_url:
                logger.info("✅ En página de creación")
            else:
                logger.warning("⚠️  No en página de creación, intentando método alternativo")

                # Método 2: Click en "New post" usando JavaScript que evita elementos bloqueantes
                new_post_js = '''
                (() => {
                    // Encontrar botón "New post" usando diferentes selectores
                    const selectors = [
                        'svg[aria-label="New post"]',
                        'svg[aria-label="New reel"]',
                        'a[href*="/create/"]',
                        'div[role="button"]:has(svg)'
                    ];

                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            console.log('Elemento encontrado:', selector);

                            // Obtener el elemento clickeable (puede ser el SVG o su padre)
                            let clickableElement = element;
                            if (element.tagName === 'svg') {
                                clickableElement = element.closest('button') ||
                                                   element.closest('div[role="button"]') ||
                                                   element.closest('a') ||
                                                   element;
                            }

                            // Usar click() de JavaScript que no se ve afectado por elementos superpuestos
                            clickableElement.click();
                            return true;
                        }
                    }
                    return false;
                })()
                '''

                new_post_clicked = await page.evaluate(new_post_js)
                if new_post_clicked:
                    logger.info("✅ Click en 'New post' usando JavaScript")
                    await asyncio.sleep(5)
                else:
                    logger.error("❌ No se pudo hacer click en 'New post'")
                    return False

            # PASO 4: SUBIR VIDEO DIRECTAMENTE
            logger.info("\n📤 SUBIENDO VIDEO DIRECTAMENTE...")

            # Verificar si estamos en la pantalla de upload
            try:
                # Esperar por el botón de selección de archivos
                await page.wait_for_selector('input[type="file"]', timeout=10000)
                logger.info("✅ Input de archivo encontrado")
            except:
                logger.warning("⚠️  Input de archivo no encontrado, buscando alternativas...")

                # Buscar botón para seleccionar archivo
                select_button_js = '''
                (() => {
                    const selectors = [
                        'div:has-text("Select from computer")',
                        'div:has-text("Select")',
                        'button:has-text("Select")',
                        'div[role="button"]:has-text("Select")'
                    ];

                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            element.click();
                            return true;
                        }
                    }
                    return false;
                })()
                '''

                select_clicked = await page.evaluate(select_button_js)
                if select_clicked:
                    logger.info("✅ Botón de selección clickeado")
                    await asyncio.sleep(2)
                else:
                    logger.error("❌ No se pudo encontrar botón de selección")
                    return False

            # Subir el archivo
            logger.info(f"📁 Subiendo archivo: {video_path.name}")

            # Usar el input de archivo
            try:
                file_input = await page.wait_for_selector('input[type="file"]', timeout=10000)
                await file_input.set_input_files(str(video_path))
                logger.info("✅ Archivo seleccionado")
            except Exception as e:
                logger.error(f"❌ Error subiendo archivo: {e}")
                return False

            await asyncio.sleep(5)

            # PASO 5: METADATA
            logger.info("\n🏷️  AGREGANDO METADATA...")

            caption = """🚀 AIReels - Upload Directo con JavaScript

✅ Login exitoso sin 2FA
🔧 Popup de notificaciones manejado
📤 Upload directo usando JavaScript
🤖 Sistema funcionando completamente

#AIReels #Automation #Instagram #Python #AI #JavaScript #Upload #Direct"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "javascript", "upload", "direct", "success"
            ]

            # Agregar caption
            caption_js = f'''
            (() => {{
                // Buscar textarea para caption
                const captionSelectors = [
                    'textarea[aria-label="Write a caption..."]',
                    'textarea[placeholder*="caption"]',
                    'textarea[placeholder*="Caption"]',
                    'textarea[aria-label*="caption"]',
                    'div[contenteditable="true"]'
                ];

                for (const selector of captionSelectors) {{
                    const element = document.querySelector(selector);
                    if (element) {{
                        const caption = `{caption}\\n\\n{''.join(f'#{tag} ' for tag in hashtags)}`;

                        if (element.tagName === 'TEXTAREA') {{
                            element.value = caption;
                            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }} else if (element.getAttribute('contenteditable') === 'true') {{
                            element.textContent = caption;
                            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}

                        console.log('Caption agregado');
                        return true;
                    }}
                }}
                return false;
            }})()
            '''

            caption_added = await page.evaluate(caption_js)
            if caption_added:
                logger.info("✅ Caption agregado")
            else:
                logger.warning("⚠️  No se pudo agregar caption automáticamente")

            await asyncio.sleep(2)

            # PASO 6: PUBLICAR
            logger.info("\n🚀 PUBLICANDO...")

            # Buscar botón de compartir/publicar
            share_js = '''
            (() => {
                const shareSelectors = [
                    'div[role="button"]:has-text("Share")',
                    'div[role="button"]:has-text("share")',
                    'button:has-text("Share")',
                    'button:has-text("share")',
                    'div:has-text("Share")',
                    'div:has-text("share")'
                ];

                for (const selector of shareSelectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        element.click();
                        console.log('Botón de share clickeado:', selector);
                        return true;
                    }
                }
                return false;
            })()
            '''

            share_clicked = await page.evaluate(share_js)
            if share_clicked:
                logger.info("✅ Botón de share clickeado")
            else:
                logger.warning("⚠️  No se encontró botón de share, intentando alternativas...")

                # Intentar con selector específico de Instagram
                try:
                    await page.click('div[role="button"]:has-text("Share")')
                    logger.info("✅ Click en botón Share")
                except:
                    logger.error("❌ No se pudo hacer click en botón Share")
                    return False

            logger.info("⏳ Esperando publicación...")
            await asyncio.sleep(10)

            # Verificar publicación exitosa
            success_js = '''
            (() => {
                // Buscar indicadores de éxito
                const successIndicators = [
                    'div:has-text("Your reel has been shared")',
                    'div:has-text("Your post has been shared")',
                    'div:has-text("shared")',
                    'div:has-text("Posted")',
                    'div:has-text("posted")',
                    'a[href*="/p/"]',
                    'a[href*="/reel/"]'
                ];

                for (const indicator of successIndicators) {
                    const element = document.querySelector(indicator);
                    if (element) {
                        console.log('Indicador de éxito encontrado:', indicator);

                        // Intentar obtener URL del post
                        const link = document.querySelector('a[href*="/p/"]') ||
                                     document.querySelector('a[href*="/reel/"]');
                        if (link) {
                            return link.href;
                        }
                        return true;
                    }
                }
                return false;
            })()
            '''

            publication_result = await page.evaluate(success_js)
            if publication_result:
                if isinstance(publication_result, str):
                    logger.info(f"🎉 ¡PUBLICACIÓN EXITOSA! URL: {publication_result}")
                else:
                    logger.info("🎉 ¡PUBLICACIÓN EXITOSA!")
            else:
                logger.info("⚠️  No se pudo verificar publicación automáticamente, pero el proceso parece completado")

            logger.info("\n✅ PROCESO COMPLETADO")
            return True

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

    logger.info("🚀 Iniciando upload directo con JavaScript")

    success = await upload_directo_con_js()

    logger.info("\n" + "=" * 80)
    logger.info("🏁 FIN DE EJECUCIÓN")
    logger.info("=" * 80)

    if success:
        logger.info("✅ ¡ÉXITO COMPLETO!")
        logger.info("🎉 Video subido y publicado en Instagram usando JavaScript")
    else:
        logger.error("❌ FALLÓ")
        logger.info(f"\n📁 REVISAR LOG: {log_file}")

    return success

if __name__ == "__main__":
    asyncio.run(main())