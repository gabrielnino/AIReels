#!/usr/bin/env python3
"""
EJECUTAR UPLOAD SIMPLIFICADO - Enfoque directo y práctico
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
print("🚀 EJECUTAR UPLOAD SIMPLIFICADO")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def ejecutar_upload():
    """Ejecutar upload de manera simplificada."""

    print("🎯 OBJETIVO: Subir video a Instagram de manera práctica")
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
        print(f"✅ 2FA: DESHABILITADO (configurado en Instagram)")

        # Verificar video
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            print("❌ No hay videos disponibles")
            return False

        video_path = videos[0]
        print(f"✅ Video: {video_path.name}")

        # Configurar navegador - BALANCE ENTRE VISIBILIDAD Y VELOCIDAD
        config = BrowserConfig(
            headless=False,      # VISIBLE para ver qué pasa
            slow_mo=100,         # Suficiente para ver, no demasiado lento
            timeout=180000,      # 3 minutos
            browser_type=BrowserType.CHROMIUM
        )

        print("✅ Navegador configurado (visible, velocidad balanceada)")

        # Crear browser service
        browser_service = BrowserService(config)

        try:
            # INICIALIZAR NAVEGADOR
            print("\n🖥️  INICIALIZANDO NAVEGADOR...")
            await browser_service.initialize()
            page = browser_service.page
            print("✅ Navegador inicializado")

            # MANEJAR LOGIN CON EL MÓDULO EXISTENTE
            print("\n🔐 USANDO MÓDULO DE LOGIN EXISTENTE...")

            # Usar el browser service para login (ya tiene lógica incorporada)
            # El BrowserService ya debería manejar login si está configurado
            print("⚠️  El navegador cargará Instagram automáticamente")
            print("⚠️  Si hay login pendiente, se hará automáticamente")
            print("⚠️  Si hay popup de notificaciones, haz click en 'Not Now' MANUALMENTE")

            # Dar tiempo para que el usuario vea y actúe si es necesario
            print("\n⏳ Esperando 10 segundos para que veas la página...")
            for i in range(10, 0, -1):
                print(f"   {i}...", end='\r')
                await asyncio.sleep(1)
            print("   Continuando...          ")

            # Configurar metadata
            caption = """🚀 AIReels - Upload Simplificado

✅ Enfoque práctico y directo
🔧 Usando módulos existentes
🎯 Objetivo: Subir video a Instagram

#AIReels #Automation #Instagram #Python #AI #Upload #Simplified"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "simplified", "practical"
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

            # Resumen
            print("\n" + "=" * 60)
            print("📋 RESUMEN - LISTO PARA INTENTAR UPLOAD")
            print("=" * 60)
            print(f"1. Navegador: Abierto y visible")
            print(f"2. Login: Debería estar hecho o pendiente")
            print(f"3. Video: {video_path.name}")
            print(f"4. Si hay popup 'Notifications': Click en 'Not Now'")
            print(f"5. Luego el script intentará upload automáticamente")

            print("\n⏳ Iniciando proceso de upload en 5 segundos...")
            for i in range(5, 0, -1):
                print(f"   {i}...", end='\r')
                await asyncio.sleep(1)
            print("   🚀 INICIANDO...          ")

            # INTENTAR UPLOAD
            print("\n📤 INTENTANDO UPLOAD...")
            upload_result = await video_uploader.upload_video(video_info)

            print(f"   • Status: {upload_result.status}")
            print(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                print("❌ Upload falló")
                print("⚠️  Posibles causas:")
                print("   1. No estás logueado en Instagram")
                print("   2. Hay un popup bloqueando")
                print("   3. Instagram cambió su interfaz")
                print("\n🔧 SUGERENCIA: Revisa el navegador manualmente")
                return False

            print("✅ Upload exitoso")

            # METADATA
            print("\n🏷️  METADATA...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")

            # PUBLICACIÓN
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

            return True

        except Exception as e:
            print(f"❌ Error durante ejecución: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            print("\n🔧 VERIFICA MANUALMENTE EL NAVEGADOR")
            print("   1. ¿Estás logueado en Instagram?")
            print("   2. ¿Hay algún popup o mensaje?")
            print("   3. ¿Puedes hacer upload manualmente?")
            return False

        finally:
            print("\n⚠️  Navegador mantenido abierto para verificación")
            print("   Cierra el navegador cuando hayas terminado")

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

    print("🚀 Ejecutando upload simplificado")
    print("⚠️  INSTRUCCIONES IMPORTANTES:")
    print("   1. El navegador se abrirá visible")
    print("   2. Si hay popup 'Turn on Notifications':")
    print("      • Haz click en 'Not Now' MANUALMENTE")
    print("   3. El script intentará el upload automáticamente")
    print("   4. Si falla, revisa el navegador para diagnóstico")
    print()

    success = await ejecutar_upload()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡ÉXITO COMPLETO!")
        print("🎉 Video subido y publicado en Instagram")
    else:
        print("❌ FALLÓ")
        print("\n🔧 DIAGNÓSTICO:")
        print("   1. Revisa el navegador abierto")
        print("   2. Verifica si estás logueado")
        print("   3. Si hay errores, anótalos para corregir")
        print("   4. Intenta hacer upload manualmente para referencia")

    return success

if __name__ == "__main__":
    asyncio.run(main())