#!/usr/bin/env python3
"""
UPLOAD A INSTAGRAM con 2FA interactivo

Este script ejecuta el flujo COMPLETO de upload a Instagram:
1. Login con 2FA interactivo (pide código en tiempo real)
2. Upload de video REAL
3. Publicación REAL

⚠️  ACCIONES REALES: Login, upload y publicación REALES
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Configurar path - usar directorio actual y ruta absoluta
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))
sys.path.insert(0, str(current_dir))

print("=" * 80)
print("🚀 UPLOAD A INSTAGRAM - Flujo completo con 2FA interactivo")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def upload_completo():
    """Ejecutar flujo completo de upload con 2FA interactivo."""

    print("🎯 OBJETIVO: Subir video REAL a Instagram")
    print("🔧 INCLUYE: Login + 2FA interactivo + Upload + Publicación")
    print()

    try:
        # 1. Importar módulos
        print("1. 📦 IMPORTANDO MÓDULOS...")
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.auth.login_manager import InstagramLoginManager
        from src.upload.video_uploader import VideoUploader, VideoInfo
        from src.upload.metadata_handler import MetadataHandler, VideoMetadata
        from src.upload.publisher import Publisher

        print("✅ Módulos importados")

        # 2. Cargar configuración
        print("\n2. 🔐 CARGANDO CONFIGURACIÓN...")
        from dotenv import load_dotenv
        env_path = current_dir / "instagram-upload" / ".env.instagram"
        print(f"   • Cargando configuración desde: {env_path}")
        load_dotenv(str(env_path))

        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')

        if not username or not password:
            print("❌ ERROR: Credenciales no configuradas")
            return False

        print(f"   • Usuario: {username}")
        print(f"   • Contraseña configurada: {'*' * len(password)}")

        # 3. Verificar video
        print("\n3. 🎥 VERIFICANDO VIDEO...")
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        print(f"   • Buscando videos en: {videos_dir}")
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            print("❌ ERROR: No hay videos en instagram-upload/videos/to_upload/")
            return False

        video_path = videos[0]
        print(f"✅ Video encontrado: {video_path.name}")
        print(f"   • Tamaño: {video_path.stat().st_size / 1024:.1f} KB")

        # 4. Configurar metadata
        print("\n4. 🏷️  CONFIGURANDO METADATA...")
        caption = """🚀 AIReels - Upload Automatizado Funcionando

✅ Sistema de automatización activo
🔧 Python + Playwright + Instagram API
🤖 Upload completamente automatizado

#AIReels #Automation #Instagram #Python #AI #Upload #RealTime #Demo"""

        hashtags = [
            "aireels", "automation", "instagram", "python",
            "ai", "upload", "realtime", "demo", "bot",
            "automatizacion", "programacion", "testing"
        ]

        print(f"✅ Metadata configurada:")
        print(f"   • Caption: {caption[:60]}...")
        print(f"   • Hashtags: {', '.join(hashtags[:5])}...")

        # 5. Configurar navegador VISIBLE
        print("\n5. ⚙️  CONFIGURANDO NAVEGADOR...")
        config = BrowserConfig(
            headless=False,      # VISIBLE para ver el proceso
            slow_mo=200,         # Pausa para ver mejor
            timeout=120000,      # 2 minutos timeout
            browser_type=BrowserType.CHROMIUM
        )

        print(f"✅ Navegador configurado:")
        print(f"   • Headless: {config.headless} (VISIBLE)")
        print(f"   • Slow mo: {config.slow_mo}ms")

        # 6. Mostrar resumen y pedir confirmación
        print("\n" + "=" * 60)
        print("🚨 RESUMEN DE ACCIONES REALES")
        print("=" * 60)
        print("\n📋 LO QUE VA A PASAR:")
        print(f"   1. Login REAL en Instagram: {username}")
        print(f"   2. 2FA interactivo (pedirá código en tiempo real)")
        print(f"   3. Upload REAL: {video_path.name}")
        print(f"   4. Publicación REAL en tu perfil")

        print("\n⚠️  ADVERTENCIAS:")
        print("   • Se usará tu cuenta REAL")
        print("   • El video será PÚBLICO")
        print("   • Instagram puede detectar automatización")

        print("\n⏳ Iniciando en 10 segundos (Ctrl+C para cancelar)...")
        try:
            for i in range(10, 0, -1):
                print(f"   {i}...", end='\r')
                await asyncio.sleep(1)
            print("   🚀 INICIANDO...          ")
        except asyncio.CancelledError:
            print("\n❌ EJECUCIÓN CANCELADA")
            return False

        # 7. INICIAR PROCESO REAL
        print("\n6. 🔓 INICIANDO PROCESO REAL...")
        browser_service = BrowserService(config)

        try:
            # A. INICIALIZAR NAVEGADOR
            print("\nA. 🖥️  INICIALIZANDO NAVEGADOR...")
            await browser_service.initialize()
            print("✅ Navegador inicializado (visible)")

            # B. LOGIN CON 2FA INTERACTIVO
            print("\nB. 🔐 LOGIN CON 2FA INTERACTIVO...")
            print("   ⚠️  ATENCIÓN: Se abrirá Instagram y pedirá 2FA")
            print("   📱 Prepara tu app de autenticación o SMS")

            login_manager = InstagramLoginManager()

            # Modificar temporalmente para entrada interactiva de 2FA
            import sys
            original_stdin = sys.stdin

            print("\n   🔢 Cuando aparezca, ingresa el código 2FA de 6 dígitos")
            print("   ⏱️  El código expira en 60 segundos")

            # Ejecutar login
            login_success = await login_manager.login()

            if not login_success:
                print("❌ LOGIN FALLÓ")
                print("   • Revisa credenciales")
                print("   • Código 2FA puede haber expirado")
                print("   • Instagram puede haber bloqueado")
                return False

            print("✅ LOGIN EXITOSO CON 2FA")
            print("   • Sesión autenticada")
            print("   • Cookies guardadas")

            # C. PREPARAR COMPONENTES DE UPLOAD
            print("\nC. 🎥 PREPARANDO UPLOAD...")

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

            # Crear componentes con el browser_service
            video_uploader = VideoUploader(browser_service=browser_service)
            metadata_handler = MetadataHandler(browser_service=browser_service)
            publisher = Publisher(browser_service=browser_service)

            print("✅ Componentes de upload preparados")

            # D. UPLOAD REAL DE VIDEO
            print("\nD. 📤 UPLOAD REAL DE VIDEO...")
            print(f"   • Video: {video_path.name}")

            upload_result = await video_uploader.upload_video(video_info)

            print(f"   • Status: {upload_result.status}")
            print(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                print("❌ UPLOAD FALLÓ")
                return False

            print("✅ UPLOAD EXITOSO")
            print(f"   • Duración: {upload_result.duration_seconds:.1f}s")

            # E. METADATA REAL
            print("\nE. 🏷️  METADATA REAL...")

            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ METADATA FALLÓ")
                return False

            print("✅ METADATA INGRESADA")

            # F. PUBLICACIÓN REAL
            print("\nF. 🚀 PUBLICACIÓN REAL...")
            print("   ⚠️  ¡ÚLTIMA OPORTUNIDAD PARA CANCELAR!")
            print("   ⏳ Publicando en 5 segundos...")

            for i in range(5, 0, -1):
                print(f"   {i}...", end='\r')
                await asyncio.sleep(1)

            publication_result = await publisher.publish_post()

            print(f"   • Status: {publication_result.status}")
            print(f"   • Mensaje: {publication_result.message}")

            if not publication_result.success:
                print("❌ PUBLICACIÓN FALLÓ")
                return False

            print("🎉 ¡PUBLICACIÓN EXITOSA!")
            if publication_result.post_url:
                print(f"🔗 URL del post: {publication_result.post_url}")

            # G. RESUMEN FINAL
            print("\nG. 📊 RESUMEN FINAL...")
            print(f"   • Login: EXITOSO")
            print(f"   • Upload: {upload_result.duration_seconds:.1f}s")
            print(f"   • Publicación: {publication_result.duration_seconds:.1f}s")
            print(f"   • Total: {upload_result.duration_seconds + publication_result.duration_seconds:.1f}s")

            # H. TOMAR SCREENSHOT FINAL
            print("\nH. 📸 TOMANDO SCREENSHOT FINAL...")
            screenshot_path = "instagram_upload_completado.png"
            page = browser_service.page
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ Screenshot: {screenshot_path}")

            return True

        except Exception as e:
            print(f"\n❌ ERROR DURANTE EJECUCIÓN: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # I. CERRAR NAVEGADOR
            print("\nI. 🧹 CERRANDO NAVEGADOR...")
            await browser_service.close()
            print("✅ Navegador cerrado")

    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en ejecución: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""

    inicio = time.time()
    print("🚀 Iniciando upload completo a Instagram...")
    print("⚠️  Este script ejecutará acciones REALES")
    print()

    success = await upload_completo()
    fin = time.time()

    duracion = fin - inicio

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN - UPLOAD A INSTAGRAM")
    print("=" * 80)

    if success:
        print("✅ ¡UPLOAD COMPLETADO EXITOSAMENTE!")
        print(f"\n⏱️  Duración total: {duracion:.1f} segundos")

        print("\n🎯 LOGRADO:")
        print("   • Login REAL con 2FA ✓")
        print("   • Upload REAL de video ✓")
        print("   • Publicación REAL en Instagram ✓")
        print("   • Screenshot tomado ✓")

        print("\n📄 ARCHIVOS GENERADOS:")
        print("   • instagram_upload_completado.png")
        print("   • instagram-upload/data/instagram_cookies.json")

        print("\n🚀 ¡VIDEO PUBLICADO EN INSTAGRAM!")
    else:
        print("⚠️  EJECUCIÓN CON ERRORES")
        print(f"\n⏱️  Duración: {duracion:.1f} segundos")

        print("\n🔧 POSIBLES SOLUCIONES:")
        print("   1. Revisa credenciales en .env.instagram")
        print("   2. Verifica código 2FA (expira en 60s)")
        print("   3. Intenta login manual primero")
        print("   4. Instagram puede bloquear automatización")

    print(f"\n⏰ Fin: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())