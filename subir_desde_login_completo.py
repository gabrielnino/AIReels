#!/usr/bin/env python3
"""
SUBIR VIDEO DESDE LOGIN COMPLETO

Este script asume que:
1. YA ESTÁS LOGEADO en Instagram (después de 2FA y "Trust this device")
2. El navegador está en la página principal de Instagram
3. Solo necesita subir y publicar el video

🚨 INSTRUCCIONES:
1. En el navegador ABIERTO, haz click MANUALMENTE en "Trust this device"
2. Espera a que cargue la página principal de Instagram (icono de casa)
3. NO cierres el navegador
4. Ejecuta este script
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
print("🚀 SUBIR VIDEO - Desde Login Completo")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def subir_video_desde_login():
    """Subir video asumiendo login ya completado."""

    print("🎯 OBJETIVO: Subir video (login ya completado)")
    print()

    # Instrucciones para el usuario
    print("⚠️  VERIFICA ANTES DE CONTINUAR:")
    print("   1. Navegador ABIERTO con Instagram")
    print("   2. YA hiciste click en 'Trust this device'")
    print("   3. Estás en página principal de Instagram (icono de casa)")
    print("   4. NO cierres el navegador")
    print()

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
        print(f"✅ Usuario configurado: {username}")

        # Verificar video
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            print("❌ No hay videos disponibles")
            return False

        video_path = videos[0]
        print(f"✅ Video encontrado: {video_path.name}")
        print(f"   • Tamaño: {video_path.stat().st_size / 1024:.1f} KB")

        # Configurar navegador - INICIAR NUEVO (pero visible)
        print("\n⚙️  CONFIGURANDO NAVEGADOR...")
        config = BrowserConfig(
            headless=False,      # VISIBLE
            slow_mo=200,         # Para ver mejor
            timeout=120000,      # 2 minutos
            browser_type=BrowserType.CHROMIUM
        )

        browser_service = BrowserService(config)

        try:
            # Inicializar navegador (abrirá nuevo navegador)
            print("\n🖥️  INICIANDO NUEVO NAVEGADOR...")
            print("⚠️  Se abrirá un SEGUNDO navegador")
            print("   El PRIMER navegador (con login) debe seguir abierto")
            await browser_service.initialize()
            print("✅ Navegador inicializado")

            # Obtener página
            page = browser_service.page

            # NAVEGAR A INSTAGRAM (debería estar ya logueado si hay cookies)
            print("\n🌐 NAVEGANDO A INSTAGRAM...")
            await page.goto('https://www.instagram.com/')
            await asyncio.sleep(3)

            # Verificar si ya estamos logueados (por cookies)
            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
                print("✅ Ya logueado en Instagram (cookies funcionaron)")
            except:
                print("⚠️  No parece estar logueado")
                print("   El primer navegador debe permanecer abierto")
                print("   Continuando de todos modos...")

            # Configurar metadata
            print("\n🏷️  CONFIGURANDO METADATA...")

            caption = """🚀 AIReels - Upload Automatizado desde Login Completo

✅ Login con 2FA exitoso
✅ 'Trust this device' completado
🔧 Subida automática funcionando
🤖 Sistema en producción

#AIReels #Automation #Instagram #Python #AI #Upload #Production #Live"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "production", "live", "demo",
                "automatizacion", "programacion", "testing"
            ]

            print(f"✅ Metadata configurada")

            # Preparar componentes
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

            print("✅ Componentes de upload preparados")

            # Resumen antes de ejecutar
            print("\n" + "=" * 60)
            print("🚨 RESUMEN DE ACCIONES")
            print("=" * 60)
            print(f"📋 LO QUE VA A PASAR:")
            print(f"   1. Navegar a página de upload")
            print(f"   2. Seleccionar video: {video_path.name}")
            print(f"   3. Subir video")
            print(f"   4. Ingresar metadata")
            print(f"   5. Publicar en Instagram")

            print("\n⏳ Iniciando upload en 5 segundos...")
            for i in range(5, 0, -1):
                print(f"   {i}...", end='\r')
                await asyncio.sleep(1)
            print("   🚀 SUBIENDO...          ")

            # UPLOAD
            print("\n📤 SUBIENDO VIDEO...")
            upload_result = await video_uploader.upload_video(video_info)

            print(f"   • Status: {upload_result.status}")
            print(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                print("❌ Upload falló")
                return False

            print("✅ Upload exitoso")
            print(f"   • Duración: {upload_result.duration_seconds:.1f}s")

            # METADATA
            print("\n🏷️  METADATA...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")

            # PUBLICACIÓN
            print("\n🚀 PUBLICANDO...")
            print("⚠️  ¡VIDEO SE PUBLICARÁ EN INSTAGRAM!")

            publication_result = await publisher.publish_post()

            print(f"   • Status: {publication_result.status}")
            print(f"   • Mensaje: {publication_result.message}")

            if not publication_result.success:
                print("❌ Publicación falló")
                return False

            print("🎉 ¡PUBLICACIÓN EXITOSA!")
            if publication_result.post_url:
                print(f"🔗 URL del post: {publication_result.post_url}")

            return True

        except Exception as e:
            print(f"❌ Error durante upload: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # Preguntar si cerrar navegador
            print("\n❓ ¿Cerrar navegador? (S/N)")
            # En entorno no interactivo, no cerrar por seguridad
            print("⚠️  Navegador NO cerrado (modo automático)")
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

    print("🚀 Preparando upload de video a Instagram...")
    print()

    success = await subir_video_desde_login()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡VIDEO SUBIDO Y PUBLICADO!")
        print("🎉 El video ahora está en Instagram")
        print("\n📊 RESUMEN:")
        print("   • Login: Completado manualmente")
        print("   • 'Trust this device': Click manual")
        print("   • Upload: Automático")
        print("   • Publicación: Automática")
    else:
        print("⚠️  SUBIDA FALLÓ")
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("   1. Asegúrate de estar logueado en Instagram")
        print("   2. Verifica que el video exista")
        print("   3. Intenta hacer upload manualmente primero")

    return success

if __name__ == "__main__":
    asyncio.run(main())