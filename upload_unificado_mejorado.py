#!/usr/bin/env python3
"""
UPLOAD UNIFICADO MEJORADO - Usa MISMO navegador para login y upload
Con manejo robusto de popups de notificaciones

Este script:
1. Crea UN solo navegador
2. Hace login en Instagram (sin 2FA, ya deshabilitado)
3. Usa el MISMO navegador para upload
4. Publica el video
5. Maneja popups de notificaciones en cada paso

🚨 2FA DESHABILITADO - Login simple con usuario/contraseña
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
print("🚀 UPLOAD UNIFICADO MEJORADO - Manejo robusto de popups")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def hacer_login_directo(page, username, password):
    """Hacer login directamente en la página."""
    print("🔐 Haciendo login directo en Instagram...")

    # Navegar a Instagram
    await page.goto('https://www.instagram.com/')
    await page.wait_for_timeout(3000)

    # Verificar si ya estamos logueados
    current_url = page.url
    if "/accounts/login" not in current_url:
        print("✅ Ya estamos logueados (cookies existentes)")
        return True

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
            print(f"✅ Username field: {selector}")
            username_filled = True
            break
        except:
            continue

    if not username_filled:
        print("❌ No se encontró campo de username")
        return False

    # Intentar password
    password_filled = False
    for selector in password_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            await page.fill(selector, password)
            print(f"✅ Password field: {selector}")
            password_filled = True
            break
        except:
            continue

    if not password_filled:
        print("❌ No se encontró campo de password")
        return False

    # Intentar botón de login
    login_clicked = False
    for selector in login_button_selectors:
        try:
            await page.wait_for_selector(selector, timeout=5000)
            await page.click(selector)
            print(f"✅ Login button: {selector}")
            login_clicked = True
            break
        except:
            continue

    if not login_clicked:
        print("❌ No se encontró botón de login")
        return False

    # Esperar login
    await page.wait_for_timeout(5000)

    # Verificar login exitoso
    print("🔍 Verificando login exitoso...")

    current_url = page.url
    print(f"ℹ️  URL después de login: {current_url}")

    if "/accounts/login" not in current_url:
        print("✅ Login exitoso - no estamos en página de login")
        return True

    print("❌ Login falló - aún en página de login")
    return False

async def _manejar_popup_notificaciones(page):
    """Manejar popup de notificaciones de Instagram de forma robusta."""

    # Selectores para popup de notificaciones
    popup_selectors = [
        'div[role="dialog"]',
        'div[role="alertdialog"]',
        'div[data-testid*="notification"]',
        'div[data-testid*="Notification"]',
        'div:has-text("Turn on Notifications")',
        'div:has-text("Turn On Notifications")',
        'div:has-text("Notifications")',
        'div:has-text("notifications")',
        'div:has-text("Get notifications")',
        'div:has-text("Allow notifications")',
        'div:has-text("Stay updated with notifications")',
        'div:has-text("Stay updated")',
        'div:has-text("Get notified")',
        'div:has-text("Enable notifications")',
        'div[class*="notification"]',
        'div[class*="Notification"]',
        'div[class*="popup"]',
        'div[class*="Popup"]',
        'div[class*="modal"]',
        'div[class*="Modal"]',
        'div[aria-modal="true"]',
        'div[data-visualcompletion="ignore"]'
    ]

    # Botones para rechazar notificaciones
    not_now_buttons = [
        'button:has-text("Not Now")',
        'button:has-text("Not now")',
        'button:has-text("Cancel")',
        'button:has-text("Later")',
        'button:has-text("Not Now")[tabindex="0"]',
        'button:has-text("Not now")[tabindex="0"]',
        'div[role="button"]:has-text("Not Now")',
        'div[role="button"]:has-text("Not now")',
        'div[role="button"]:has-text("Cancel")',
        'div[role="button"]:has-text("Later")',
        'div:has-text("Not Now"):visible',
        'div:has-text("Not now"):visible',
        'span:has-text("Not Now"):visible',
        'span:has-text("Not now"):visible',
        'button[data-testid*="not-now"]',
        'button[data-testid*="cancel"]',
        'button[aria-label*="Not Now"]',
        'button[aria-label*="Not now"]'
    ]

    try:
        # Buscar popup
        for popup_selector in popup_selectors:
            try:
                popup = page.locator(popup_selector).first
                if await popup.is_visible(timeout=2000):
                    print(f"⚠️  Popup detectado: {popup_selector}")

                    # Buscar y hacer click en "Not Now" o similar
                    for button_selector in not_now_buttons:
                        try:
                            button = page.locator(button_selector).first
                            if await button.is_visible(timeout=1000):
                                print(f"✅ Botón encontrado: {button_selector}")
                                await button.click()
                                print("✅ Click en 'Not Now'")
                                await asyncio.sleep(2)
                                return True
                        except:
                            continue

                    # Si no encontró botón específico, intentar cerrar de otras formas
                    print("⚠️  No se encontró botón específico, intentando alternativas...")

                    # Intentar hacer click fuera del popup
                    try:
                        await page.mouse.click(10, 10)  # Click en esquina
                        print("✅ Click fuera del popup")
                        await asyncio.sleep(2)
                        return True
                    except:
                        pass

                    # Intentar presionar Escape
                    try:
                        await page.keyboard.press('Escape')
                        print("✅ Presionado Escape")
                        await asyncio.sleep(2)
                        return True
                    except:
                        pass

            except:
                continue

        return False  # No se encontró popup

    except Exception as e:
        print(f"⚠️  Error manejando popup: {e}")
        return False

async def verificar_popup_antes_de_accion(page, accion_nombre):
    """Verificar popup de notificaciones antes de realizar una acción."""
    print(f"🔍 Verificando popups antes de {accion_nombre}...")
    await asyncio.sleep(1)

    popup_manejado = await _manejar_popup_notificaciones(page)
    if popup_manejado:
        print(f"✅ Popup de notificaciones cerrado antes de {accion_nombre}")

    return popup_manejado

async def upload_unificado_mejorado():
    """Flujo completo mejorado con manejo robusto de popups."""

    print("🎯 OBJETIVO: Login y upload en mismo navegador con manejo de popups")
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
        password = os.environ.get('INSTAGRAM_PASSWORD')

        if not username or not password:
            print("❌ Credenciales no configuradas")
            return False

        print(f"✅ Usuario: {username}")
        print(f"✅ 2FA: DESHABILITADO (configurado en Instagram)")

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
            slow_mo=200,         # Para ver mejor
            timeout=180000,      # 3 minutos
            browser_type=BrowserType.CHROMIUM
        )

        print("✅ Navegador configurado (visible)")

        # Crear browser service
        browser_service = BrowserService(config)

        # INICIALIZAR NAVEGADOR (UNICO)
        print("\n🖥️  INICIALIZANDO NAVEGADOR ÚNICO...")
        await browser_service.initialize()
        page = browser_service.page
        print("✅ Navegador inicializado")

        # HACER LOGIN DIRECTO (en este mismo navegador)
        print("\n🔐 HACIENDO LOGIN DIRECTO...")
        login_success = await hacer_login_directo(page, username, password)

        if not login_success:
            print("❌ Login falló")
            return False

        print("✅ Login exitoso en navegador único")

        # MANEJAR POPUP DE NOTIFICACIONES INMEDIATAMENTE DESPUÉS DEL LOGIN
        print("\n🔍 MANEJANDO POPUP DE NOTIFICACIONES POST-LOGIN...")
        await asyncio.sleep(3)
        notificaciones_post_login = await _manejar_popup_notificaciones(page)
        if notificaciones_post_login:
            print("✅ Popup de notificaciones cerrado después del login")
        else:
            print("ℹ️  No se detectó popup de notificaciones post-login")

        # Configurar metadata
        caption = """🚀 AIReels - Upload Automatizado Mejorado

✅ Login sin 2FA exitoso
🔧 Mismo navegador para login y upload
🤖 Manejo robusto de popups de notificaciones
✅ Sistema funcionando autónomamente

#AIReels #Automation #Instagram #Python #AI #Upload #No2FA"""

        hashtags = [
            "aireels", "automation", "instagram", "python",
            "ai", "upload", "autonomous", "no2fa", "demo", "popups"
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

        # Crear componentes de upload CON EL MISMO BROWSER_SERVICE
        video_uploader = VideoUploader(browser_service=browser_service)
        metadata_handler = MetadataHandler(browser_service=browser_service)
        publisher = Publisher(browser_service=browser_service)

        print("✅ Componentes creados con mismo browser_service")

        # Resumen antes de upload
        print("\n" + "=" * 60)
        print("🚨 RESUMEN - LISTO PARA UPLOAD")
        print("=" * 60)
        print(f"📋 USANDO MISMO NAVEGADOR PARA:")
        print(f"   1. Login (completado)")
        print(f"   2. Upload: {video_path.name}")
        print(f"   3. Metadata")
        print(f"   4. Publicación")
        print(f"   5. Manejo de popups en cada paso")

        print("\n⏳ Iniciando upload en 5 segundos...")
        for i in range(5, 0, -1):
            print(f"   {i}...", end='\r')
            await asyncio.sleep(1)
        print("   🚀 SUBIENDO...          ")

        # PASO 1: UPLOAD con verificación de popups
        print("\n📤 SUBIENDO VIDEO...")

        # Verificar popup ANTES de upload
        await verificar_popup_antes_de_accion(page, "upload")

        # Hacer upload
        upload_result = await video_uploader.upload_video(video_info)

        # Verificar popup DESPUÉS de upload
        await verificar_popup_antes_de_accion(page, "post-upload")

        print(f"   • Status: {upload_result.status}")
        print(f"   • Mensaje: {upload_result.message}")

        if not upload_result.success:
            print("❌ Upload falló")
            return False

        print("✅ Upload exitoso")
        print(f"   • Duración: {upload_result.duration_seconds:.1f}s")

        # PASO 2: METADATA con verificación de popups
        print("\n🏷️  METADATA...")

        # Verificar popup ANTES de metadata
        await verificar_popup_antes_de_accion(page, "metadata")

        metadata_success = await metadata_handler.enter_all_metadata(metadata)

        if not metadata_success:
            print("❌ Metadata falló")
            return False

        print("✅ Metadata ingresada")

        # PASO 3: PUBLICACIÓN con verificación de popups
        print("\n🚀 PUBLICANDO...")
        print("⚠️  ¡VIDEO SE PUBLICARÁ EN INSTAGRAM!")

        # Verificar popup ANTES de publicación
        await verificar_popup_antes_de_accion(page, "publicación")

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

    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return False
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

    print("🚀 Iniciando upload unificado mejorado")
    print("⚠️  2FA DEBE ESTAR DESHABILITADO EN INSTAGRAM")
    print()

    success = await upload_unificado_mejorado()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡ÉXITO COMPLETO!")
        print("🎉 Video subido y publicado en Instagram")
        print("\n📊 LOGRO:")
        print("   • Login exitoso ✓")
        print("   • Mismo navegador para todo ✓")
        print("   • Upload automático ✓")
        print("   • Manejo robusto de popups ✓")
        print("   • Publicación automática ✓")
    else:
        print("❌ FALLÓ")
        print("\n🔧 POSIBLES CAUSAS:")
        print("   1. Credenciales incorrectas")
        print("   2. Instagram aún pide 2FA")
        print("   3. Problemas de red/conexión")
        print("   4. Selectores de Instagram cambiaron")
        print("   5. Popup de notificaciones bloqueó la acción")

    return success

if __name__ == "__main__":
    asyncio.run(main())