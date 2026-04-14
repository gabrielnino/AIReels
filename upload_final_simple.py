#!/usr/bin/env python3
"""
UPLOAD FINAL SIMPLE - Versión enfocada en lo esencial

🚨 2FA DESHABILITADO - Login simple
🔧 Manejo de popups incluido
🎯 Enfoque en subir el video
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))

print("=" * 80)
print("🚀 UPLOAD FINAL SIMPLE")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def upload_simple_final():
    """Versión simple y directa."""

    print("🎯 OBJETIVO: Subir video a Instagram (2FA deshabilitado)")
    print()

    try:
        # Importar
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.upload.video_uploader import VideoUploader, VideoInfo
        from src.upload.metadata_handler import MetadataHandler, VideoMetadata
        from src.upload.publisher import Publisher

        print("✅ Módulos importados")

        # Configuración
        from dotenv import load_dotenv
        env_path = current_dir / "instagram-upload" / ".env.instagram"
        load_dotenv(str(env_path))

        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')

        if not username or not password:
            print("❌ Credenciales no configuradas")
            return False

        print(f"✅ Usuario: {username}")
        print("✅ 2FA: Deshabilitado (según configuración de Instagram)")

        # Video
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            print("❌ No hay videos")
            return False

        video_path = videos[0]
        print(f"✅ Video: {video_path.name}")

        # Navegador
        config = BrowserConfig(
            headless=False,
            slow_mo=300,  # Más lento para debugging
            timeout=240000,  # 4 minutos
            browser_type=BrowserType.CHROMIUM
        )

        browser_service = BrowserService(config)

        try:
            # 1. INICIAR NAVEGADOR
            print("\n1. 🖥️  INICIANDO NAVEGADOR...")
            await browser_service.initialize()
            page = browser_service.page
            print("✅ Navegador listo")

            # 2. LOGIN DIRECTO
            print("\n2. 🔐 LOGIN EN INSTAGRAM...")

            # Ir a Instagram
            await page.goto('https://www.instagram.com/')
            await asyncio.sleep(3)

            # Rellenar campos
            await page.fill('input[name="email"]', username)
            await page.fill('input[name="pass"]', password)

            # Click login
            await page.click('div[role="button"]:has-text("Log in")')
            print("✅ Login enviado")

            # Esperar
            await asyncio.sleep(5)

            # 3. MANEJAR "TURN ON NOTIFICATIONS - NOT NOW"
            print("\n3. 🔔 MANEJANDO NOTIFICACIONES...")

            # Buscar popup de notificaciones
            try:
                not_now_button = page.locator('button:has-text("Not Now")').first
                if await not_now_button.is_visible(timeout=5000):
                    await not_now_button.click()
                    print("✅ Click en 'Not Now'")
                    await asyncio.sleep(2)
            except:
                print("ℹ️  No hay popup de notificaciones")

            # 4. VERIFICAR LOGIN
            print("\n4. ✓ VERIFICANDO LOGIN...")
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
                print("✅ Login exitoso - en página principal")
            except:
                print("⚠️  No se pudo verificar login, continuando...")

            # 5. SUBIR VIDEO
            print("\n5. 📤 SUBIENDO VIDEO...")

            # Preparar video y metadata
            caption = "🚀 AIReels - Upload automatizado #AIReels #Automation #Instagram"
            hashtags = ["aireels", "automation", "instagram", "python", "ai", "upload"]

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

            # Crear uploader
            uploader = VideoUploader(browser_service=browser_service)
            metadata_handler = MetadataHandler(browser_service=browser_service)
            publisher = Publisher(browser_service=browser_service)

            # Intentar upload
            print("   • Intentando upload...")
            upload_result = await uploader.upload_video(video_info)

            if not upload_result.success:
                print(f"❌ Upload falló: {upload_result.message}")
                return False

            print(f"✅ Upload exitoso: {upload_result.message}")

            # 6. METADATA
            print("\n6. 🏷️  METADATA...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")

            # 7. PUBLICAR
            print("\n7. 🚀 PUBLICANDO...")
            print("⚠️  ¡VIDEO SE PUBLICARÁ EN INSTAGRAM!")

            publication_result = await publisher.publish_post()

            if not publication_result.success:
                print(f"❌ Publicación falló: {publication_result.message}")
                return False

            print(f"🎉 ¡PUBLICADO! {publication_result.message}")
            if publication_result.post_url:
                print(f"🔗 URL: {publication_result.post_url}")

            return True

        finally:
            print("\n🧹 Finalizando...")
            # await browser_service.close()  # Mantener abierto para diagnóstico

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Ejecutando upload final simple...")
    print("⚠️  Asegúrate de que 2FA esté deshabilitado en Instagram")
    print()

    success = await upload_simple_final()

    print("\n" + "=" * 80)
    if success:
        print("✅ ¡ÉXITO! Video publicado en Instagram")
        print("\n🎯 LOGRADO:")
        print("   • Login sin 2FA")
        print("   • Manejo de 'Not Now'")
        print("   • Upload automático")
        print("   • Publicación automática")
    else:
        print("❌ FALLÓ")
        print("\n💡 SUGERENCIAS:")
        print("   1. Verifica que 2FA esté deshabilitado")
        print("   2. Revisa credenciales")
        print("   3. Intenta login manual primero")

    return success

if __name__ == "__main__":
    asyncio.run(main())