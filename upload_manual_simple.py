#!/usr/bin/env python3
"""
UPLOAD MANUAL SIMPLE - Login manual + upload automático

Este script:
1. Abre navegador para que hagas login MANUALMENTE
2. Después del login, haz click en 'Not Now' si aparece popup
3. Luego el script hace el upload AUTOMÁTICAMENTE
"""

import asyncio
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Cargar configuración
current_dir = Path(__file__).parent
env_path = current_dir / "instagram-upload" / ".env.instagram"
load_dotenv(str(env_path))

username = os.environ.get('INSTAGRAM_USERNAME')
password = os.environ.get('INSTAGRAM_PASSWORD')

print("=" * 80)
print("🚀 UPLOAD MANUAL SIMPLE - Login manual + upload automático")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

if not username or not password:
    print("❌ Credenciales no configuradas en .env.instagram")
    print("   Configura INSTAGRAM_USERNAME y INSTAGRAM_PASSWORD")
    exit(1)

print(f"✅ Usuario: {username}")
print(f"✅ 2FA debe estar DESHABILITADO en Instagram")
print()

async def upload_manual_simple():
    """Login manual, luego upload automático."""

    import sys
    sys.path.insert(0, str(current_dir / "instagram-upload"))

    from playwright.async_api import async_playwright

    print("🎯 INSTRUCCIONES PASO A PASO:")
    print("   1. El navegador se abrirá en Instagram")
    print("   2. Haz login MANUALMENTE (usuario y contraseña)")
    print("   3. Si aparece popup 'Turn on Notifications':")
    print("      • Haz click en 'Not Now'")
    print("   4. Espera a que aparezca la página principal")
    print("   5. El script hará el upload AUTOMÁTICAMENTE")
    print()

    print("⏳ Preparando navegador...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        page = await browser.new_page()

        try:
            # PASO 1: IR A INSTAGRAM
            print("\n🌐 Navegando a Instagram...")
            await page.goto('https://www.instagram.com/')
            await asyncio.sleep(3)

            print("✅ Instagram cargado")
            print("\n" + "=" * 60)
            print("🖱️  ¡AHORA HAZ LOGIN MANUALMENTE!")
            print("=" * 60)
            print("   1. Ingresa usuario y contraseña")
            print("   2. Haz click en 'Log In'")
            print("   3. Si hay popup 'Notifications': 'Not Now'")
            print("   4. Espera a que cargue la página principal")
            print()

            # Esperar a que el usuario haga login manualmente
            print("⏳ Esperando que hagas login manualmente...")
            print("   Tienes 60 segundos para completar el login")
            print("   El contador comenzará después de 10 segundos...")
            await asyncio.sleep(10)

            for i in range(60, 0, -1):
                print(f"   Tiempo restante: {i} segundos", end='\r')
                await asyncio.sleep(1)
            print("\n✅ Continuando con upload automático...")

            # Verificar si estamos logueados (intentar)
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
                print("✅ Parece que estás logueado (Home encontrado)")
            except:
                print("⚠️  No se pudo verificar login automáticamente")
                print("   Continuando de todos modos...")

            # PASO 2: USAR LOS MÓDULOS DE UPLOAD
            print("\n🔧 CARGANDO MÓDULOS DE UPLOAD...")

            from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
            from src.upload.video_uploader import VideoUploader, VideoInfo
            from src.upload.metadata_handler import MetadataHandler, VideoMetadata
            from src.upload.publisher import Publisher

            print("✅ Módulos cargados")

            # Verificar video
            videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
            videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

            if not videos:
                print("❌ No hay videos disponibles")
                return False

            video_path = videos[0]
            print(f"✅ Video encontrado: {video_path.name}")

            # Crear un BrowserService usando la página existente
            # Necesitamos un pequeño hack para reusar la página
            print("🔗 Conectando con navegador existente...")

            # Configurar browser service
            config = BrowserConfig(
                headless=False,
                slow_mo=100,
                timeout=180000,
                browser_type=BrowserType.CHROMIUM
            )

            # Crear browser service manualmente
            browser_service = BrowserService(config)

            # Hack: asignar nuestra página existente al browser service
            # Esto no es ideal pero funciona para este caso
            browser_service._browser = browser
            browser_service._context = browser.contexts[0]
            browser_service._page = page
            browser_service._initialized = True

            print("✅ Browser service configurado con página existente")

            # Configurar metadata
            caption = """🚀 AIReels - Upload con Login Manual

✅ Login manual exitoso
🔧 Upload automático funcionando
🎯 Video subido a Instagram

#AIReels #Automation #Instagram #Python #AI #Upload #ManualLogin"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "manuallogin", "working"
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

            print("✅ Componentes de upload creados")

            # PASO 3: INTENTAR UPLOAD
            print("\n📤 INTENTANDO UPLOAD AUTOMÁTICO...")
            print(f"📁 Archivo: {video_path.name}")

            upload_result = await video_uploader.upload_video(video_info)

            print(f"   • Status: {upload_result.status}")
            print(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                print("❌ Upload falló")
                print("\n🔧 DIAGNÓSTICO:")
                print("   1. ¿Estás seguramente logueado?")
                print("   2. ¿Ves la página principal de Instagram?")
                print("   3. ¿Hay algún popup bloqueando?")
                print("   4. ¿Puedes hacer upload manualmente?")
                return False

            print("✅ Upload exitoso")
            await asyncio.sleep(3)

            # PASO 4: METADATA
            print("\n🏷️  METADATA...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")
            await asyncio.sleep(2)

            # PASO 5: PUBLICAR
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

            # Esperar para ver resultado
            print("⏳ Esperando 10 segundos para ver post publicado...")
            await asyncio.sleep(10)

            print("\n✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
            return True

        except Exception as e:
            print(f"❌ Error durante ejecución: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            print("\n⚠️  Navegador mantenido abierto para verificación")
            print("   Cierra el navegador cuando hayas terminado")

async def main():
    """Función principal."""

    print("🚀 INICIANDO UPLOAD MANUAL SIMPLE")
    print()

    success = await upload_manual_simple()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡ÉXITO COMPLETO!")
        print("🎉 Video subido y publicado en Instagram")
    else:
        print("❌ FALLÓ")
        print("\n🔧 PRÓXIMOS PASOS:")
        print("   1. Revisa el navegador para ver qué pasó")
        print("   2. Intenta hacer upload manualmente para referencia")
        print("   3. Anota cualquier error o mensaje que veas")
        print("   4. Verifica credenciales y si 2FA está deshabilitado")

    return success

if __name__ == "__main__":
    asyncio.run(main())