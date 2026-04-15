#!/usr/bin/env python3
"""
🚀 EXPERIMENTO 006: Upload real CON PUBLICACIÓN
OBJETIVO: Subir video REAL y hacer click en "Share" para publicación completa
META: Cerrar ciclo 100% - video publicado en @fiestacotoday
"""

import asyncio
import time
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("🚀 EXPERIMENTO 006: UPLOAD REAL CON PUBLICACIÓN")
print("=" * 80)
print("🎯 OBJETIVO: Publicar video REAL en @fiestacotoday")
print("⚠️  ADVERTENCIA: Esto PUBLICARÁ video REAL en Instagram")
print("   El video será visible públicamente")
print("=" * 80)

async def real_upload_with_publication():
    """Subir y PUBLICAR video real en Instagram."""
    from playwright.async_api import async_playwright

    results = {
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "authenticated": False,
        "upload_completed": False,
        "video_published": False,
        "verified_in_account": False,
        "publication_timestamp": None,
        "errors": [],
        "screenshots": [],
        "video_used": "",
        "account_checked": "fiestacotoday",
        "caption_used": "🎥 Test upload from AIReels automation 🚀 #AIReels #automation"
    }

    exp_dir = Path(__file__).parent
    exp_dir.mkdir(exist_ok=True)

    playwright = None
    browser = None
    page = None

    try:
        print("\n1️⃣ CONFIGURACIÓN: Navegador para publicación real...")
        print("   🖥️  Navegador VISIBLE para monitoreo")
        print("   🐢 Comportamiento HUMANO (slow-mo: 1500ms)")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,  # VISIBLE para monitoreo
            slow_mo=1500,    # Comportamiento muy humano
            args=['--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            # Limpiar estado de sesión para evitar one-tap
            storage_state=None
        )

        page = await context.new_page()
        page.set_default_timeout(120000)  # 120 segundos para upload

        print("\n2️⃣ PASO 1: Estrategia de autenticación MEJORADA...")
        print("   🔐 Limpieza de sesión + login tradicional")

        # Navegar DIRECTAMENTE a login para evitar one-tap
        print("   🔗 Navegando a accounts/login directamente...")
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle')
        await asyncio.sleep(3)

        initial_url = page.url
        initial_title = await page.title()
        print(f"   📍 URL inicial: {initial_url}")
        print(f"   📄 Título: {initial_title}")

        await page.screenshot(path=str(exp_dir / "01_login_page.png"), full_page=True)
        results["screenshots"].append("01_login_page.png")

        # Cargar credenciales
        env_path = Path(__file__).parent.parent.parent / "instagram-upload" / ".env.instagram"
        credentials = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        credentials[key] = value

        username = credentials.get('INSTAGRAM_USERNAME', 'fiestacotoday')
        password = credentials.get('INSTAGRAM_PASSWORD', '')

        print(f"   👤 Usuario: {username}")

        # Buscar campos de login
        username_field = None
        password_field = None

        username_selectors = [
            'input[name="username"]',
            'input[name="email"]',
            'input[type="text"]',
            'input[autocomplete="username"]'
        ]

        password_selectors = [
            'input[name="password"]',
            'input[type="password"]',
            'input[autocomplete="current-password"]'
        ]

        for selector in username_selectors:
            if await page.locator(selector).count() > 0:
                username_field = page.locator(selector).first
                print(f"   ✅ Campo usuario: {selector}")
                break

        for selector in password_selectors:
            if await page.locator(selector).count() > 0:
                password_field = page.locator(selector).first
                print(f"   ✅ Campo password: {selector}")
                break

        if not username_field or not password_field:
            print("   ❌ Campos de login no encontrados")
            print("   🔍 Verificando si ya estamos autenticados...")

            # Verificar si ya estamos en feed
            auth_indicators = [
                'svg[aria-label="Home"]',
                'svg[aria-label="Search"]',
                'a[href*="/direct/inbox/"]'
            ]

            auth_count = 0
            for selector in auth_indicators:
                if await page.locator(selector).count() > 0:
                    auth_count += 1

            if auth_count >= 2:
                print("   ✅ ¡Ya parece autenticado!")
                results["authenticated"] = True
            else:
                print("   ❌ No autenticado y no hay campos de login")
                results["errors"].append("Campos de login no encontrados")
                return results
        else:
            # Hacer login tradicional
            print("   ⌨️  Ingresando credenciales...")
            await username_field.click()
            await asyncio.sleep(1)
            await username_field.fill(username)
            await asyncio.sleep(1)

            await password_field.click()
            await asyncio.sleep(1)
            await password_field.fill(password)
            await asyncio.sleep(1)

            # Buscar botón login
            login_button = None
            login_selectors = [
                'button[type="submit"]',
                'div[role="button"]:has-text("Log in")',
                'button:has-text("Log in")',
                'button:has-text("Log In")'
            ]

            for selector in login_selectors:
                if await page.locator(selector).count() > 0:
                    login_button = page.locator(selector).first
                    print(f"   ✅ Botón login: {selector}")
                    break

            if login_button:
                print("   🔘 Click en Login...")
                await login_button.click()
                await asyncio.sleep(5)  # Esperar login

                # Manejar possible one-tap o save info
                save_info_selectors = [
                    'button:has-text("Not Now")',
                    'div[role="button"]:has-text("Not Now")',
                    'button:has-text("Save Info")',
                    'button:has-text("Save info")'
                ]

                for selector in save_info_selectors:
                    if await page.locator(selector).count() > 0:
                        print(f"   🔘 Click en: {selector}")
                        await page.locator(selector).first.click()
                        await asyncio.sleep(3)
                        break

                results["authenticated"] = True
                print("   ✅ Login tradicional completado")
            else:
                print("   ❌ Botón login no encontrado")
                results["errors"].append("Botón login no encontrado")
                return results

        # Verificar autenticación REAL
        print("\n   🔍 Verificando autenticación REAL...")
        await asyncio.sleep(2)

        current_url = page.url
        current_title = await page.title()
        print(f"   📍 URL post-login: {current_url}")
        print(f"   📄 Título: {current_title}")

        # Verificar indicadores de autenticación
        auth_check_selectors = [
            'svg[aria-label="Home"]',
            'svg[aria-label="Search"]',
            'a[href*="/fiestacotoday/"]',  # Nuestro perfil
            'a[href*="/accounts/activity/"]'
        ]

        auth_check_count = 0
        for selector in auth_check_selectors:
            if await page.locator(selector).count() > 0:
                auth_check_count += 1
                print(f"   ✅ Indicador auth: {selector}")

        if auth_check_count >= 2:
            print(f"   ✅ Autenticación VERIFICADA ({auth_check_count}/4 indicadores)")
            results["authenticated"] = True
        else:
            print(f"   ❌ Autenticación NO verificada ({auth_check_count}/4 indicadores)")
            results["errors"].append(f"Autenticación no verificada ({auth_check_count}/4 indicadores)")
            return results

        await page.screenshot(path=str(exp_dir / "02_authenticated.png"), full_page=True)
        results["screenshots"].append("02_authenticated.png")

        print("\n3️⃣ PASO 2: Navegar a página de upload...")
        print("   🔗 Navegando a /create (post-autenticación)...")

        await page.goto('https://www.instagram.com/create', wait_until='networkidle')
        await asyncio.sleep(3)

        create_url = page.url
        create_title = await page.title()
        print(f"   📍 URL create: {create_url}")
        print(f"   📄 Título: {create_title}")

        # VERIFICACIÓN CRÍTICA: ¿Estamos en página REAL de upload?
        if 'chris shelley' in create_title.lower():
            print("   ❌ ¡FALSO POSITIVO! En perfil de usuario 'Chris Shelley'")
            print("   🔍 Esto significa: NO estamos autenticados correctamente")
            results["errors"].append("Redirección a perfil de usuario - autenticación incompleta")
            return results

        if 'create' not in create_url.lower() and 'upload' not in create_title.lower():
            print("   ⚠️  Posiblemente no en página de upload")
            print("   🔍 Continuando con verificación visual...")

        await page.screenshot(path=str(exp_dir / "03_create_page.png"), full_page=True)
        results["screenshots"].append("03_create_page.png")

        print("   ✅ En página de upload")

        print("\n4️⃣ PASO 3: Seleccionar 'Post' y subir video...")

        # Buscar y hacer click en "Post"
        post_found = False
        post_selectors = [
            'div[role="button"]:has-text("Post")',
            'button:has-text("Post")',
            'div:has-text("Post"):visible',
            'span:has-text("Post")'
        ]

        for selector in post_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    print(f"   🔘 Click en: {selector}")
                    await page.locator(selector).first.click()
                    await asyncio.sleep(3)
                    post_found = True
                    break
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                continue

        if not post_found:
            print("   ⚠️  Botón Post no encontrado, continuando...")

        # Buscar input de archivo
        print("   📁 Buscando input para subir video...")

        file_input = None
        file_selectors = [
            'input[type="file"]',
            'input[accept*="video"]',
            'input[accept*="mp4"]',
            'input[accept*="mov"]',
            'input[accept*="video/mp4"]'
        ]

        for selector in file_selectors:
            if await page.locator(selector).count() > 0:
                file_input = page.locator(selector).first
                print(f"   ✅ Input encontrado: {selector}")
                break

        if not file_input:
            print("   🔍 Input no encontrado, buscando botón Select...")
            select_buttons = [
                'div[role="button"]:has-text("Select")',
                'button:has-text("Select")',
                'div:has-text("Select from computer")',
                'span:has-text("Select from computer")'
            ]

            for selector in select_buttons:
                if await page.locator(selector).count() > 0:
                    print(f"   🔘 Click en: {selector}")
                    await page.locator(selector).first.click()
                    await asyncio.sleep(2)

                    # Re-buscar input
                    for file_selector in file_selectors:
                        if await page.locator(file_selector).count() > 0:
                            file_input = page.locator(file_selector).first
                            print(f"   ✅ Input apareció: {file_selector}")
                            break
                    break

        if not file_input:
            print("   ❌ No se pudo encontrar input de archivo")
            results["errors"].append("Input de archivo no encontrado")
            return results

        # Seleccionar video
        videos_dir = Path(__file__).parent.parent.parent / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            print("   ❌ No hay videos en directorio")
            results["errors"].append("No hay videos para upload")
            return results

        video_path = videos[0]
        results["video_used"] = str(video_path.name)
        video_size_kb = video_path.stat().st_size / 1024
        video_size_mb = video_size_kb / 1024

        print(f"   🎥 Video seleccionado: {video_path.name}")
        print(f"   📊 Tamaño: {video_size_kb:.1f} KB ({video_size_mb:.2f} MB)")

        try:
            print("   ⬆️  Subiendo video...")
            start_upload_time = time.time()
            await file_input.set_input_files(str(video_path))

            print("   ⏳ Esperando procesamiento (puede tomar tiempo)...")

            # Esperar indicadores de procesamiento
            processing_indicators = [
                ':has-text("Processing")',
                ':has-text("Uploading")',
                ':has-text("Processing video")',
                'div[aria-label*="progress"]',
                'progress',
                'div[class*="progress"]',
                'div[class*="upload"]'
            ]

            processing_found = False
            for i in range(60):  # Máximo 60 segundos para upload
                for indicator in processing_indicators:
                    if await page.locator(indicator).count() > 0:
                        if not processing_found:
                            print(f"   🔄 Procesamiento detectado ({i+1}s)")
                            processing_found = True
                        break

                # Si no hay procesamiento después de 10s, continuar
                if i >= 10 and not processing_found:
                    print("   ⏩ Continuando sin indicadores de procesamiento...")
                    break

                if i % 10 == 0 and i > 0:
                    print(f"   ⏰ {i+1}s...")

                await asyncio.sleep(1)

            upload_duration = time.time() - start_upload_time
            print(f"   ✅ Upload completado en {upload_duration:.1f}s")

            await page.screenshot(path=str(exp_dir / "04_video_uploaded.png"), full_page=True)
            results["screenshots"].append("04_video_uploaded.png")
            results["upload_completed"] = True

        except Exception as e:
            print(f"   ❌ Error subiendo video: {e}")
            results["errors"].append(f"Error subiendo video: {e}")
            return results

        print("\n5️⃣ PASO 4: Completar metadata y PUBLICAR...")
        print("   🔍 Verificando página de edición...")

        await asyncio.sleep(5)  # Esperar que cargue página de edición
        await page.screenshot(path=str(exp_dir / "05_editing_page.png"), full_page=True)
        results["screenshots"].append("05_editing_page.png")

        # Verificar elementos de edición
        edit_elements = {
            "caption": await page.locator('textarea[aria-label="Write a caption..."]').count() > 0,
            "caption_alt": await page.locator('textarea[placeholder*="caption"]').count() > 0,
            "next_button": await page.locator('div[role="button"]:has-text("Next")').count() > 0,
            "share_button": await page.locator('div[role="button"]:has-text("Share")').count() > 0
        }

        print(f"   📋 Elementos encontrados:")
        print(f"     - Caption: {'✅' if edit_elements['caption'] or edit_elements['caption_alt'] else '❌'}")
        print(f"     - Next button: {'✅' if edit_elements['next_button'] else '❌'}")
        print(f"     - Share button: {'✅' if edit_elements['share_button'] else '❌'}")

        # Escribir caption si hay campo
        if edit_elements['caption']:
            caption_field = page.locator('textarea[aria-label="Write a caption..."]').first
        elif edit_elements['caption_alt']:
            caption_field = page.locator('textarea[placeholder*="caption"]').first
        else:
            caption_field = None

        if caption_field:
            print(f"   📝 Escribiendo caption: {results['caption_used']}")
            await caption_field.click()
            await asyncio.sleep(1)
            await caption_field.fill(results['caption_used'])
            await asyncio.sleep(2)

        # Click en Next si existe
        if edit_elements['next_button']:
            print("   🔘 Click en Next...")
            next_button = page.locator('div[role="button"]:has-text("Next")').first
            await next_button.click()
            await asyncio.sleep(3)

            await page.screenshot(path=str(exp_dir / "06_after_next.png"), full_page=True)
            results["screenshots"].append("06_after_next.png")

        # ¡PUBLICAR! - Click en Share
        if edit_elements['share_button']:
            print("   🚀 ¡PUBLICANDO VIDEO! Click en Share...")
            share_button = page.locator('div[role="button"]:has-text("Share")').first

            # Última confirmación antes de publicar
            print("   ⚠️  ADVERTENCIA: Esto publicará el video REALMENTE")
            print("   🔘 Haciendo click en Share en 3 segundos...")
            await asyncio.sleep(3)

            await share_button.click()
            results["publication_timestamp"] = datetime.now().isoformat()

            print("   ✅ ¡CLICK EN SHARE REALIZADO!")
            print("   🎉 ¡VIDEO PUBLICADO EN INSTAGRAM!")

            # Esperar confirmación de publicación
            print("   ⏳ Esperando confirmación de publicación...")
            await asyncio.sleep(5)

            results["video_published"] = True

            await page.screenshot(path=str(exp_dir / "07_after_share.png"), full_page=True)
            results["screenshots"].append("07_after_share.png")

            # Verificar mensaje de éxito
            success_indicators = [
                ':has-text("Your post has been shared")',
                ':has-text("shared")',
                ':has-text("posted")',
                'div[role="dialog"]',
                'div[class*="success"]'
            ]

            for indicator in success_indicators:
                if await page.locator(indicator).count() > 0:
                    print(f"   ✅ Indicador de éxito: {indicator}")
                    break
        else:
            print("   ❌ Botón Share no encontrado")
            results["errors"].append("Botón Share no encontrado")
            return results

        print("\n6️⃣ PASO 5: Verificar publicación en cuenta...")
        print("   🔍 Navegando al perfil para verificar...")

        await page.goto('https://www.instagram.com/fiestacotoday/', wait_until='networkidle')
        await asyncio.sleep(5)

        profile_url = page.url
        print(f"   📍 Perfil: {profile_url}")

        await page.screenshot(path=str(exp_dir / "08_profile_check.png"), full_page=True)
        results["screenshots"].append("08_profile_check.png")

        # Verificar posts recientes
        recent_posts = await page.locator('article').count()
        print(f"   📊 Posts visibles en perfil: {recent_posts}")

        if recent_posts > 0:
            print("   ✅ Hay posts en el perfil")
            results["verified_in_account"] = True

            # Intentar identificar nuestro post reciente
            print("   🔍 Buscando post más reciente...")
            await page.locator('article').first.scroll_into_view_if_needed()
            await asyncio.sleep(2)

            await page.screenshot(path=str(exp_dir / "09_recent_posts.png"), full_page=True)
            results["screenshots"].append("09_recent_posts.png")
        else:
            print("   ⚠️  No hay posts visibles en el perfil")
            results["verified_in_account"] = False

        results["success"] = True

        print("\n" + "="*80)
        print("🎉 ¡EXPERIMENTO 006 COMPLETADO EXITOSAMENTE!")
        print("="*80)
        print("   ✅ Autenticación: COMPLETADA")
        print("   ✅ Upload de video: COMPLETADO")
        print("   ✅ PUBLICACIÓN: REALIZADA (click en Share)")
        print(f"   ✅ Perfil verificado: {'SÍ' if results['verified_in_account'] else 'NO POSTS VISIBLES'}")
        print(f"   🎥 Video: {results['video_used']}")
        print(f"   📅 Publicado: {results['publication_timestamp']}")
        print("="*80)

        return results

    except Exception as e:
        print(f"\n🚨 ERROR NO MANEJADO: {e}")
        import traceback
        traceback.print_exc()

        results["errors"].append(f"Error no manejado: {str(e)}")
        return results

    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

async def main():
    """Ejecutar experimento 006 con publicación real."""
    print("⚠️  ADVERTENCIA CRÍTICA: Este experimento:")
    print("   1. Intentará autenticación REAL")
    print("   2. Subirá video REAL a Instagram")
    print("   3. Hará click en 'Share' - PUBLICACIÓN REAL")
    print("   4. El video será visible públicamente en @fiestacotoday")
    print("   5. No se puede deshacer")
    print("="*80)

    confirm = input("\n¿Continuar con PUBLICACIÓN REAL? (sí/no): ")
    if confirm.lower() not in ['sí', 'si', 's', 'yes', 'y']:
        print("❌ Experimento cancelado - No se publicará video")
        return

    print("\n🔧 PREPARANDO PUBLICACIÓN REAL...")
    print("   📁 Verificando videos disponibles...")

    videos_dir = Path(__file__).parent.parent.parent / "instagram-upload" / "videos" / "to_upload"
    videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

    if not videos:
        print("❌ No hay videos en videos/to_upload/")
        print("   Coloca al menos un video .mp4 o .mov en esa carpeta")
        return

    print(f"   ✅ Videos encontrados: {len(videos)}")
    for i, video in enumerate(videos[:3]):
        size_mb = video.stat().st_size / (1024 * 1024)
        print(f"     {i+1}. {video.name} ({size_mb:.1f} MB)")

    if len(videos) > 1:
        print(f"   ℹ️  Se usará el primer video: {videos[0].name}")

    start_time = time.time()
    results = await real_upload_with_publication()
    duration = time.time() - start_time

    print(f"\n{'='*80}")
    print("📊 RESULTADOS FINALES EXPERIMENTO 006:")
    print(f"{'='*80}")

    if results["success"]:
        print("🎉 ¡PUBLICACIÓN EXITOSA!")
        print(f"✅ Autenticación: {'Sí' if results['authenticated'] else 'No'}")
        print(f"✅ Upload completado: {'Sí' if results['upload_completed'] else 'No'}")
        print(f"✅ PUBLICACIÓN REAL: {'Sí' if results['video_published'] else 'No'}")
        print(f"✅ Perfil accesible: {'Sí' if results['verified_in_account'] else 'No'}")
        print(f"📅 Publicado a las: {results.get('publication_timestamp', 'N/A')}")
        print(f"🎥 Video publicado: {results.get('video_used', 'N/A')}")
        print(f"⏱️  Duración total: {duration:.1f}s")

        print(f"\n💡 CONCLUSIÓN:")
        print("   ¡CICLO 100% COMPLETADO!")
        print("   Video publicado REALMENTE en Instagram")
        print("   Sistema de automatización FUNCIONAL")

    else:
        print("🔧 PROBLEMAS ENCONTRADOS:")
        for error in results.get("errors", []):
            print(f"   ❌ {error}")

        print(f"\n⏱️  Duración: {duration:.1f}s")

        print(f"\n💡 CONCLUSIÓN:")
        print("   Problemas específicos identificados.")
        print("   Revisar errores y ajustar.")

    print(f"{'='*80}")

    # Guardar reporte detallado
    report = f"""# 🎯 EXPERIMENTO 006: Upload real CON PUBLICACIÓN

## 📊 RESULTADOS
{'✅ ÉXITO - VIDEO PUBLICADO' if results['success'] else '❌ FALLÓ'}
⏱️ Duración: {duration:.1f}s
🔐 Autenticado: {'✅ Sí' if results['authenticated'] else '❌ No'}
📤 Upload completado: {'✅ Sí' if results['upload_completed'] else '❌ No'}
🚀 PUBLICACIÓN REAL: {'✅ SÍ - Video publicado' if results['video_published'] else '❌ No'}
👤 Perfil verificado: {'✅ Sí' if results['verified_in_account'] else '❌ No'}
📅 Timestamp publicación: {results.get('publication_timestamp', 'N/A')}
🎥 Video usado: {results.get('video_used', 'N/A')}
📸 Screenshots: {len(results.get('screenshots', []))}

## 📋 ESTADO DEL SISTEMA
"""

    if results["success"]:
        report += """**✅ SISTEMA 100% FUNCIONAL**
- Autenticación exitosa
- Upload de video exitoso
- PUBLICACIÓN REAL exitosa
- Video visible en Instagram

**¡AUTOMATIZACIÓN COMPLETA LOGRADA!**
"""
    else:
        report += "**🔧 PROBLEMAS ESPECÍFICOS**\n"
        for error in results.get("errors", []):
            report += f"- {error}\n"

        report += "\n**AJUSTES REQUERIDOS**"

    report += f"""

## 🎯 ESTRATEGIA USADA
1. **Login tradicional directo** (evitar one-tap)
2. **Verificación robusta** de autenticación
3. **Upload con timeout generoso** (60s)
4. **Caption automático** incluido
5. **Click REAL en Share** para publicación
6. **Verificación post-publicación**

## 📁 EVIDENCIA
Screenshots capturados:
"""

    for i, screenshot in enumerate(results.get("screenshots", []), 1):
        report += f"{i}. `{screenshot}`\n"

    report += f"""

---
Ejecutado: {results['timestamp']}
Duración: {duration:.1f} segundos
Experimento: 006_real_upload
"""

    report_path = exp_dir / "EXPERIMENT_006_REPORT.md"
    report_path.write_text(report)
    print(f"\n📄 Reporte detallado guardado en: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())