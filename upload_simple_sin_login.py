#!/usr/bin/env python3
"""
UPLOAD SIMPLE SIN LOGIN - Asume navegador ya abierto en Instagram logueado

INSTRUCCIONES PARA EL USUARIO:
1. En el navegador que ya tienes abierto:
   - Haz click MANUALMENTE en "Trust this device"
   - Espera a que cargue la página principal de Instagram
   - NO cierres el navegador

2. Luego ejecuta este script
"""

import asyncio
import sys
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))

async def upload_simple():
    """Intenta upload asumiendo ya está logueado."""

    print("=" * 60)
    print("🚀 UPLOAD SIMPLE - Asume navegador ya logueado")
    print("=" * 60)
    print()
    print("⚠️  PRERREQUISITOS:")
    print("   1. Navegador ABIERTO en Instagram")
    print("   2. Ya hiciste login (incluyendo 2FA)")
    print("   3. Ya hiciste click en 'Trust this device'")
    print("   4. Estás en página principal de Instagram")
    print()

    try:
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.upload.video_uploader import VideoUploader, VideoInfo
        from src.upload.metadata_handler import MetadataHandler, VideoMetadata
        from src.upload.publisher import Publisher

        print("✅ Módulos importados")

        # Configurar navegador NUEVO
        config = BrowserConfig(
            headless=False,
            slow_mo=300,  # Más lento para ver mejor
            timeout=180000,
            browser_type=BrowserType.CHROMIUM
        )

        browser_service = BrowserService(config)

        try:
            # Iniciar NUEVO navegador
            print("🖥️  Iniciando NUEVO navegador...")
            await browser_service.initialize()

            # Ir a Instagram (debería redirigir a home si hay cookies)
            print("🌐 Navegando a Instagram...")
            page = browser_service.page
            await page.goto('https://www.instagram.com/')
            await asyncio.sleep(5)

            # Verificar si estamos logueados
            print("🔍 Verificando login...")
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
                print("✅ Parece estar logueado (icono de casa encontrado)")
            except:
                print("⚠️  No se encontró icono de casa")
                print("   Intentando continuar de todos modos...")

            # Buscar video
            videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
            videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

            if not videos:
                print("❌ No hay videos en videos/to_upload/")
                return False

            video_path = videos[0]
            print(f"✅ Video: {video_path.name}")

            # Configurar metadata simple
            caption = "🚀 AIReels - Upload automatizado #AIReels #Automation"
            hashtags = ["aireels", "automation", "instagram", "python", "ai"]

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

            print("\n🎯 INTENTANDO UPLOAD...")

            # Intentar upload
            upload_result = await uploader.upload_video(video_info)

            if not upload_result.success:
                print(f"❌ Upload falló: {upload_result.message}")
                print("⚠️  Posiblemente no estás logueado")
                return False

            print(f"✅ Upload exitoso: {upload_result.message}")

            # Metadata
            print("🏷️  Ingresando metadata...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")

            # Publicar
            print("🚀 Publicando...")
            pub_result = await publisher.publish_post()

            if not pub_result.success:
                print(f"❌ Publicación falló: {pub_result.message}")
                return False

            print(f"🎉 ¡PUBLICADO! {pub_result.message}")
            if pub_result.post_url:
                print(f"🔗 URL: {pub_result.post_url}")

            return True

        finally:
            print("\n⚠️  Manteniendo navegador abierto...")
            # await browser_service.close()  # No cerrar para diagnóstico

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Iniciando upload simple...")
    print("⚠️  Asegúrate de cumplir los prerrequisitos arriba")

    success = await upload_simple()

    print("\n" + "=" * 60)
    if success:
        print("✅ ¡ÉXITO! Video publicado en Instagram")
    else:
        print("❌ FALLÓ - Revisa los prerrequisitos")
        print("\n💡 SUGERENCIAS:")
        print("   1. Asegúrate de estar logueado en Instagram")
        print("   2. Haz click manual en 'Trust this device'")
        print("   3. Intenta hacer upload manualmente")

    return success

if __name__ == "__main__":
    asyncio.run(main())