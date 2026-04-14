#!/usr/bin/env python3
"""
UPLOAD UNIFICADO - Usa MISMO navegador para login y upload

Este script:
1. Crea UN solo navegador
2. Hace login en Instagram (sin 2FA, ya deshabilitado)
3. Usa el MISMO navegador para upload
4. Publica el video

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
print("🚀 UPLOAD UNIFICADO - Mismo navegador para login y upload")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def hacer_login_directo(page, username, password):
    """Hacer login directamente en la página."""
    print("🔐 Haciendo login directo en Instagram...")

    # Navegar a Instagram
    await page.goto('https://www.instagram.com/')
    await page.wait_for_timeout(3000)

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

    # Verificar login exitoso con múltiples selectores
    print("🔍 Verificando login exitoso...")

    selectores_login_exitoso = [
        'svg[aria-label="Home"]',
        'svg[aria-label="Instagram"]',
        'a[href="/"]',
        'a[href*="/home"]',
        'div[role="navigation"]',
        'nav',
        'div[data-testid="primary-nav"]',
        'div[class*="nav"]:visible',
        'div:has-text("Home"):visible',
        'div:has-text("Search"):visible',
        'div:has-text("Explore"):visible',
        'div:has-text("Reels"):visible',
        'div:has-text("Create"):visible',
        'div:has-text("Notifications"):visible',
        'div:has-text("Profile"):visible',
        'button[aria-label="New post"]',
        'button:has-text("Create")',
        'button:has-text("Post")'
    ]

    for selector in selectores_login_exitoso:
        try:
            await page.wait_for_selector(selector, timeout=3000)
            print(f"✅ Login exitoso - selector encontrado: {selector}")

            # Verificar también que NO estamos en página de login
            login_selectors_still_present = [
                'input[name="email"]',
                'input[name="username"]',
                'input[name="pass"]',
                'input[name="password"]',
                'button:has-text("Log in")',
                'button:has-text("Log In")'
            ]

            login_still_visible = False
            for login_selector in login_selectors_still_present:
                try:
                    element = page.locator(login_selector).first
                    if await element.is_visible(timeout=1000):
                        login_still_visible = True
                        break
                except:
                    continue

            if not login_still_visible:
                print("✅ Confirmado: No estamos en página de login")
                return True
            else:
                print("⚠️  Selectores de login aún visibles, continuando verificación...")

        except:
            continue

    # Si no encontramos selectores, verificar URL
    current_url = page.url
    print(f"ℹ️  URL actual: {current_url}")

    if "instagram.com" in current_url and "/accounts/login" not in current_url:
        print("✅ Login exitoso - URL verificado (no es página de login)")
        return True

    print("❌ No se pudo verificar login exitoso")
    return False

async def manejar_todos_los_popups(page):
    """Manejar todos los popups y elementos superpuestos de Instagram."""

    print("🔍 Buscando y manejando popups/elementos bloqueantes...")

    # 1. PRIMERO: Popup de notificaciones
    notificaciones_manejado = await _manejar_popup_notificaciones(page)
    if notificaciones_manejado:
        print("✅ Popup de notificaciones manejado")

    # Esperar un momento
    await asyncio.sleep(2)

    # 2. SEGUNDO: Buscar otros popups/dialogs
    otros_popups_manejados = await _manejar_otros_popups(page)
    if otros_popups_manejados:
        print("✅ Otros popups manejados")

    # 3. TERCERO: Buscar elementos que intercepten clicks
    elementos_manejados = await _manejar_elementos_bloqueantes(page)
    if elementos_manejados:
        print("✅ Elementos bloqueantes manejados")

    return notificaciones_manejado or otros_popups_manejados or elementos_manejados

async def _manejar_popup_notificaciones(page):
    """Manejar popup de notificaciones de Instagram."""

    # Selectores para popup de notificaciones "Turn on Notifications"
    popup_selectors = [
        'div[role="dialog"]',
        'div[role="alertdialog"]',
        'div[data-testid="notification-popup"]',
        'div[data-testid*="notification"]',
        'div[data-testid*="Notification"]',
        'div:has-text("Turn on Notifications")',
        'div:has-text("Turn On Notifications")',
        'div:has-text("Notifications")',
        'div:has-text("notifications")',
        'div:has-text("Get notifications")',
        'div:has-text("Would you like to turn on notifications")',
        'div:has-text("Allow notifications")',
        'div:has-text("Stay updated with notifications")',
        'div:has-text("Stay updated")',
        'div:has-text("Get notified")',
        'div:has-text("Enable notifications")',
        'div:has-text("Turn on")',
        'div:has-text("Turn On")',
        'div:has-text("notification")',
        'div:has-text("Notification")',
        'div[class*="notification"]',
        'div[class*="Notification"]',
        'div[class*="popup"]',
        'div[class*="Popup"]',
        'div[class*="modal"]',
        'div[class*="Modal"]',
        'div[class*="dialog"]',
        'div[class*="Dialog"]',
        'div[class*="overlay"]',
        'div[class*="Overlay"]',
        'div[data-visualcompletion="ignore"]',  # Instagram usa esto
        'div[aria-modal="true"]',  # Modales
        'div[tabindex="-1"]:visible'  # Elementos enfocados
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
        'button:has-text("Not Now")[tabindex="0"]',
        'button:has-text("Not now")[tabindex="0"]',
        'button:has-text("Cancel")[tabindex="0"]',
        'button:has-text("Later")[tabindex="0"]',
        'div[role="button"]:has-text("Not Now")',
        'div[role="button"]:has-text("Not now")',
        'div[role="button"]:has-text("Cancel")',
        'div[role="button"]:has-text("Later")',
        'div:has-text("Not Now"):visible',
        'div:has-text("Not now"):visible',
        'span:has-text("Not Now"):visible',
        'span:has-text("Not now"):visible',
        'a:has-text("Not Now"):visible',
        'a:has-text("Not now"):visible',
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
                if await popup.is_visible(timeout=3000):
                    print(f"⚠️  Popup detectado: {popup_selector}")

                    # Buscar y hacer click en "Not Now" o similar
                    for button_selector in not_now_buttons:
                        try:
                            button = page.locator(button_selector).first
                            if await button.is_visible(timeout=2000):
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

async def _manejar_otros_popups(page):
    """Manejar otros popups de Instagram (cookies, verificaciones, etc.)"""

    # Selectores para otros popups comunes
    otros_popup_selectors = [
        'div:has-text("cookie")',
        'div:has-text("Cookie")',
        'div:has-text("Accept")',
        'div:has-text("accept")',
        'div:has-text("Allow")',
        'div:has-text("allow")',
        'div:has-text("Got it")',
        'div:has-text("got it")',
        'div:has-text("OK")',
        'div:has-text("ok")',
        'div:has-text("Understand")',
        'div:has-text("understand")'
    ]

    # Botones para aceptar/cerrar
    otros_botones = [
        'button:has-text("Accept")',
        'button:has-text("accept")',
        'button:has-text("Allow")',
        'button:has-text("allow")',
        'button:has-text("OK")',
        'button:has-text("ok")',
        'button:has-text("Got it")',
        'button:has-text("got it")',
        'button:has-text("Close")',
        'button:has-text("close")',
        'button:has-text("I Understand")',
        'button:has-text("I understand")'
    ]

    manejado = False

    for popup_selector in otros_popup_selectors:
        try:
            popup = page.locator(popup_selector).first
            if await popup.is_visible(timeout=2000):
                print(f"⚠️  Otro popup detectado: {popup_selector}")

                # Buscar botón para cerrar/aceptar
                for button_selector in otros_botones:
                    try:
                        button = page.locator(button_selector).first
                        if await button.is_visible(timeout=1000):
                            print(f"✅ Botón encontrado: {button_selector}")
                            await button.click()
                            print("✅ Click en botón del popup")
                            await asyncio.sleep(1)
                            manejado = True
                            break
                    except:
                        continue

                if manejado:
                    break

        except:
            continue

    return manejado

async def _manejar_elementos_bloqueantes(page):
    """Manejar elementos que puedan estar interceptando clicks."""

    print("🔍 Buscando elementos que intercepten clicks...")

    # Buscar elementos con características de bloqueo
    selectores_bloqueantes = [
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

    manejado = False

    for selector in selectores_bloqueantes:
        try:
            elementos = await page.query_selector_all(selector)
            for i, elemento in enumerate(elementos[:5]):  # Revisar primeros 5
                try:
                    # Verificar si es visible y podría estar bloqueando
                    es_visible = await elemento.is_visible()
                    if es_visible:
                        print(f"⚠️  Elemento potencialmente bloqueante: {selector} #{i}")

                        # Intentar hacerlo invisible o moverlo
                        try:
                            # Intentar hacer click en él (podría cerrarlo)
                            await elemento.click()
                            print(f"✅ Click en elemento bloqueante")
                            await asyncio.sleep(1)
                            manejado = True
                        except:
                            # Intentar removerlo del DOM
                            try:
                                await page.evaluate('(element) => element.style.display = "none"', elemento)
                                print(f"✅ Elemento ocultado")
                                manejado = True
                            except:
                                pass

                except:
                    continue
        except:
            continue

    # Si no se manejó, intentar estrategias generales
    if not manejado:
        print("⚠️  Intentando estrategias generales...")

        # 1. Intentar hacer click en diferentes partes de la pantalla
        try:
            # Click en diferentes coordenadas
            width, height = page.viewport_size['width'], page.viewport_size['height']
            coords = [
                (width//2, height//2),  # Centro
                (width//4, height//4),  # Esquina superior izquierda
                (3*width//4, height//4),  # Esquina superior derecha
                (width//4, 3*height//4),  # Esquina inferior izquierda
                (3*width//4, 3*height//4)  # Esquina inferior derecha
            ]

            for x, y in coords:
                try:
                    await page.mouse.click(x, y)
                    print(f"✅ Click en coordenadas ({x}, {y})")
                    await asyncio.sleep(0.5)
                except:
                    continue
        except:
            pass

        # 2. Intentar varias veces Escape
        try:
            for _ in range(3):
                await page.keyboard.press('Escape')
                await asyncio.sleep(0.5)
            print("✅ Escape presionado múltiples veces")
        except:
            pass

        # 3. Intentar scroll
        try:
            await page.mouse.wheel(0, 100)
            await asyncio.sleep(0.5)
            await page.mouse.wheel(0, -100)
            print("✅ Scroll realizado")
        except:
            pass

    return manejado

async def verificar_y_manejar_popups_continuamente(page, duracion_segundos=30):
    """Verificar y manejar popups continuamente por un tiempo."""

    print(f"🔍 Verificación continua de popups por {duracion_segundos} segundos...")
    tiempo_inicio = asyncio.get_event_loop().time()

    while (asyncio.get_event_loop().time() - tiempo_inicio) < duracion_segundos:
        # Verificar popup de notificaciones
        notificaciones_manejado = await _manejar_popup_notificaciones(page)
        if notificaciones_manejado:
            print("✅ Popup de notificaciones detectado y manejado durante verificación continua")

        # Verificar otros popups
        otros_popups = await _manejar_otros_popups(page)
        if otros_popups:
            print("✅ Otro popup detectado y manejado durante verificación continua")

        # Esperar un momento antes de la siguiente verificación
        await asyncio.sleep(2)

    print("✅ Verificación continua de popups completada")

async def upload_unificado():
    """Flujo completo con un solo navegador."""

    print("🎯 OBJETIVO: Login y upload en mismo navegador")
    print()

    try:
        # Importar módulos
        import asyncio
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
            headless=False,      # VISIBLE
            slow_mo=200,         # Para ver mejor
            timeout=180000,      # 3 minutos
            browser_type=BrowserType.CHROMIUM
        )

        print("✅ Navegador configurado (visible)")

        # Crear browser service
        browser_service = BrowserService(config)

        try:
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

            # Esperar a que posible popup de notificaciones aparezca después del login
            print("\n⏳ Esperando posibles popups post-login...")
            await asyncio.sleep(5)

            # Verificar popup de notificaciones inmediatamente después del login
            print("🔍 Verificando popup de notificaciones post-login...")
            notificaciones_post_login = await _manejar_popup_notificaciones(page)
            if notificaciones_post_login:
                print("✅ Popup de notificaciones cerrado (post-login)")
            else:
                print("ℹ️  No se detectó popup post-login")

            # MANEJAR TODOS LOS POPUPS Y ELEMENTOS BLOQUEANTES
            print("\n🔍 BUSCANDO Y MANEJANDO POPUPS/ELEMENTOS BLOQUEANTES...")
            popups_manejados = await manejar_todos_los_popups(page)
            if popups_manejados:
                print("✅ Popups/elementos bloqueantes manejados")
            else:
                print("ℹ️  No se encontraron popups/elementos bloqueantes")

            # VERIFICACIÓN ESPECÍFICA PARA POPUP DE NOTIFICACIONES
            print("\n🔍 VERIFICACIÓN ESPECÍFICA: Popup de notificaciones...")
            await asyncio.sleep(2)  # Esperar a que posible popup cargue
            notificaciones_manejado = await _manejar_popup_notificaciones(page)
            if notificaciones_manejado:
                print("✅ Popup de notificaciones cerrado (verificación adicional)")
            else:
                print("ℹ️  No se detectó popup de notificaciones")

            # Configurar metadata
            caption = """🚀 AIReels - Upload Automatizado Unificado

✅ Login sin 2FA exitoso
🔧 Mismo navegador para login y upload
🤖 Sistema funcionando autónomamente

#AIReels #Automation #Instagram #Python #AI #Upload #Autonomous #No2FA"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "autonomous", "no2fa", "demo"
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
            print(f"   1. Login (ya completado)")
            print(f"   2. Upload: {video_path.name}")
            print(f"   3. Metadata")
            print(f"   4. Publicación")

            print("\n⏳ Iniciando upload en 5 segundos...")
            for i in range(5, 0, -1):
                print(f"   {i}...", end='\r')
                await asyncio.sleep(1)
            print("   🚀 SUBIENDO...          ")

            # UPLOAD
            print("\n📤 SUBIENDO VIDEO...")

            # VERIFICACIÓN ANTES DE UPLOAD: Popup de notificaciones
            print("🔍 Verificando popups antes de upload...")
            await asyncio.sleep(1)
            notificaciones_antes = await _manejar_popup_notificaciones(page)
            if notificaciones_antes:
                print("✅ Popup de notificaciones cerrado antes de upload")

            # Hacer upload con verificación continua EN PARALELO
            import asyncio
            # Crear tarea para verificación continua
            verificacion_task = asyncio.create_task(verificar_y_manejar_popups_continuamente(page, duracion_segundos=60))

            # Hacer upload
            upload_result = await video_uploader.upload_video(video_info)

            # Cancelar verificación continua
            verificacion_task.cancel()
            try:
                await verificacion_task
            except asyncio.CancelledError:
                print("✅ Verificación continua cancelada")

            # VERIFICACIÓN FINAL: Popup de notificaciones
            print("🔍 Verificación final de popups...")
            await asyncio.sleep(1)
            notificaciones_final = await _manejar_popup_notificaciones(page)
            if notificaciones_final:
                print("✅ Popup de notificaciones cerrado en verificación final")

            print(f"   • Status: {upload_result.status}")
            print(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                print("❌ Upload falló")
                return False

            print("✅ Upload exitoso")
            print(f"   • Duración: {upload_result.duration_seconds:.1f}s")

            # METADATA
            print("\n🏷️  METADATA...")

            # VERIFICACIÓN ANTES DE METADATA: Popup de notificaciones
            print("🔍 Verificando popups antes de metadata...")
            await asyncio.sleep(1)
            notificaciones_antes_metadata = await _manejar_popup_notificaciones(page)
            if notificaciones_antes_metadata:
                print("✅ Popup de notificaciones cerrado antes de metadata")

            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")

            # PUBLICACIÓN
            print("\n🚀 PUBLICANDO...")
            print("⚠️  ¡VIDEO SE PUBLICARÁ EN INSTAGRAM!")

            # VERIFICACIÓN ANTES DE PUBLICACIÓN: Popup de notificaciones
            print("🔍 Verificando popups antes de publicación...")
            await asyncio.sleep(1)
            notificaciones_antes_publicacion = await _manejar_popup_notificaciones(page)
            if notificaciones_antes_publicacion:
                print("✅ Popup de notificaciones cerrado antes de publicación")

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
            # Preguntar antes de cerrar
            print("\n⚠️  Navegador mantenido abierto para verificación")
            # await browser_service.close()

    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""

    print("🚀 Iniciando upload unificado (login + upload mismo navegador)")
    print("⚠️  2FA DEBE ESTAR DESHABILITADO EN INSTAGRAM")
    print()

    success = await upload_unificado()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡ÉXITO COMPLETO!")
        print("🎉 Video subido y publicado en Instagram")
        print("\n📊 LOGRO:")
        print("   • Login sin 2FA ✓")
        print("   • Mismo navegador para todo ✓")
        print("   • Upload automático ✓")
        print("   • Publicación automática ✓")
    else:
        print("❌ FALLÓ")
        print("\n🔧 POSIBLES CAUSAS:")
        print("   1. Credenciales incorrectas")
        print("   2. Instagram aún pide 2FA")
        print("   3. Problemas de red/conexión")
        print("   4. Selectores de Instagram cambiaron")

    return success

if __name__ == "__main__":
    asyncio.run(main())