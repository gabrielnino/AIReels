#!/usr/bin/env python3
"""
UPLOAD A INSTAGRAM con 2FA manual - Versión simplificada

Este script:
1. Pide código 2FA manualmente al inicio
2. Actualiza .env.instagram con el código
3. Ejecuta el flujo completo de upload

🚨 ACCIONES REALES: Login, upload y publicación REALES
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Configurar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))
sys.path.insert(0, str(current_dir))

print("=" * 80)
print("🚀 UPLOAD A INSTAGRAM - 2FA Manual")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

def obtener_codigo_2fa():
    """Obtener código 2FA - usar código proporcionado o pedir al usuario."""
    print("🔢 OBTENIENDO CÓDIGO 2FA")
    print("-" * 40)

    # Usar el código que el usuario ya proporcionó
    codigo_proporcionado = "688774"

    print(f"📱 Usando código 2FA proporcionado: {codigo_proporcionado}")
    print("⚠️  NOTA: Si este código ha expirado (cambia cada 30 segundos),")
    print("     necesitarás proporcionar un nuevo código.")
    print()

    # Verificar formato del código
    if len(codigo_proporcionado) != 6:
        print(f"❌ Código debe tener 6 dígitos, tiene {len(codigo_proporcionado)}")
        return None

    if not codigo_proporcionado.isdigit():
        print("❌ Código debe contener solo números")
        return None

    return codigo_proporcionado

def actualizar_codigo_2fa(codigo):
    """Actualizar archivo .env.instagram con nuevo código 2FA."""
    env_path = current_dir / "instagram-upload" / ".env.instagram"

    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Buscar y reemplazar línea de INSTAGRAM_2FA_CODE
        for i, line in enumerate(lines):
            if line.startswith('INSTAGRAM_2FA_CODE='):
                lines[i] = f'INSTAGRAM_2FA_CODE={codigo}\n'
                break

        with open(env_path, 'w') as f:
            f.writelines(lines)

        print(f"✅ Código 2FA actualizado en: {env_path}")
        return True

    except Exception as e:
        print(f"❌ Error actualizando código 2FA: {e}")
        return False

async def ejecutar_upload():
    """Ejecutar flujo completo de upload."""

    print("\n🎯 INICIANDO FLUJO DE UPLOAD")
    print("-" * 40)

    try:
        # 1. Obtener código 2FA
        codigo_2fa = obtener_codigo_2fa()
        if not codigo_2fa:
            return False

        # 2. Actualizar archivo de configuración
        if not actualizar_codigo_2fa(codigo_2fa):
            return False

        # 3. Esperar para asegurar código fresco
        print("\n⏳ Preparando ejecución (5 segundos)...")
        for i in range(5, 0, -1):
            print(f"   {i}...", end='\r')
            await asyncio.sleep(1)
        print("   ✅ Listo!          ")

        # 4. Importar módulos
        print("\n📦 IMPORTANDO MÓDULOS...")
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.auth.login_manager import InstagramLoginManager
        from src.upload.video_uploader import VideoUploader, VideoInfo
        from src.upload.metadata_handler import MetadataHandler, VideoMetadata
        from src.upload.publisher import Publisher

        print("✅ Módulos importados")

        # 5. Cargar configuración
        print("\n🔐 CARGANDO CONFIGURACIÓN...")
        from dotenv import load_dotenv
        env_path = current_dir / "instagram-upload" / ".env.instagram"
        load_dotenv(str(env_path))

        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')

        if not username or not password:
            print("❌ Credenciales no configuradas")
            return False

        print(f"✅ Usuario: {username}")

        # 6. Verificar video
        print("\n🎥 VERIFICANDO VIDEO...")
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            print("❌ No hay videos disponibles")
            return False

        video_path = videos[0]
        print(f"✅ Video seleccionado: {video_path.name}")

        # 7. Configurar metadata
        print("\n🏷️  CONFIGURANDO METADATA...")
        caption = """🚀 AIReels - Upload Automatizado

✅ Sistema funcionando en tiempo real
🔧 Python + Playwright + Automatización
🤖 Subida completa automatizada a Instagram

#AIReels #Automation #Instagram #Python #AI #Upload #RealTime"""

        hashtags = [
            "aireels", "automation", "instagram", "python",
            "ai", "upload", "realtime", "demo", "bot",
            "automatizacion", "programacion", "testing"
        ]

        print(f"✅ Metadata configurada")

        # 8. Configurar navegador VISIBLE
        print("\n⚙️  CONFIGURANDO NAVEGADOR...")
        config = BrowserConfig(
            headless=False,      # VISIBLE para ver el proceso
            slow_mo=200,         # Pausa para ver mejor
            timeout=120000,      # 2 minutos timeout
            browser_type=BrowserType.CHROMIUM
        )

        print(f"✅ Navegador configurado (visible)")

        # 9. Resumen final antes de ejecutar
        print("\n" + "=" * 60)
        print("🚨 RESUMEN FINAL - ACCIONES REALES")
        print("=" * 60)
        print(f"\n📋 LO QUE VA A PASAR:")
        print(f"   1. Login REAL en Instagram: {username}")
        print(f"   2. Usando código 2FA: {codigo_2fa}")
        print(f"   3. Upload REAL: {video_path.name}")
        print(f"   4. Publicación REAL en tu perfil")

        print("\n⚠️  ÚLTIMA CONFIRMACIÓN")
        print("⏳ Iniciando en 10 segundos (Ctrl+C para cancelar)...")
        try:
            for i in range(10, 0, -1):
                print(f"   {i}...", end='\r')
                await asyncio.sleep(1)
            print("   🚀 EJECUTANDO...          ")
        except asyncio.CancelledError:
            print("\n❌ Cancelado por el usuario")
            return False

        # 10. EJECUCIÓN REAL
        print("\n🔓 INICIANDO EJECUCIÓN REAL...")
        browser_service = BrowserService(config)

        try:
            # A. Inicializar navegador
            print("\nA. 🖥️  INICIALIZANDO NAVEGADOR...")
            await browser_service.initialize()
            print("✅ Navegador inicializado")

            # B. Login con InstagramLoginManager
            print("\nB. 🔐 LOGIN EN INSTAGRAM...")
            print(f"   • Usuario: {username}")
            print(f"   • Código 2FA: {codigo_2fa}")

            login_manager = InstagramLoginManager()
            login_success = await login_manager.login()

            if not login_success:
                print("❌ Login falló")
                print("   • Revisa credenciales o código 2FA")
                return False

            print("✅ Login exitoso")

            # C. Preparar componentes de upload
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

            # Crear componentes con el browser_service existente
            video_uploader = VideoUploader(browser_service=browser_service)
            metadata_handler = MetadataHandler(browser_service=browser_service)
            publisher = Publisher(browser_service=browser_service)

            print("✅ Componentes preparados")

            # D. Upload de video
            print("\nD. 📤 UPLOAD DE VIDEO...")
            print(f"   • Video: {video_path.name}")

            upload_result = await video_uploader.upload_video(video_info)

            print(f"   • Status: {upload_result.status}")
            print(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                print("❌ Upload falló")
                return False

            print("✅ Upload exitoso")

            # E. Ingresar metadata
            print("\nE. 🏷️  METADATA...")

            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")

            # F. Publicación final
            print("\nF. 🚀 PUBLICACIÓN...")
            print("⚠️  ¡ÚLTIMA ACCIÓN - VIDEO SE PUBLICARÁ!")

            publication_result = await publisher.publish_post()

            print(f"   • Status: {publication_result.status}")
            print(f"   • Mensaje: {publication_result.message}")

            if not publication_result.success:
                print("❌ Publicación falló")
                return False

            print("🎉 ¡PUBLICACIÓN EXITOSA!")

            if publication_result.post_url:
                print(f"🔗 URL del post: {publication_result.post_url}")

            # G. Resumen
            print("\nG. 📊 RESUMEN...")
            print(f"   • Login: EXITOSO")
            print(f"   • Upload: {upload_result.duration_seconds:.1f}s")
            print(f"   • Publicación: {publication_result.duration_seconds:.1f}s")
            print(f"   • Total: {upload_result.duration_seconds + publication_result.duration_seconds:.1f}s")

            return True

        except Exception as e:
            print(f"\n❌ ERROR DURANTE EJECUCIÓN: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # H. Cerrar navegador
            print("\nH. 🧹 CERRANDO NAVEGADOR...")
            await browser_service.close()
            print("✅ Navegador cerrado")

    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""

    inicio = time.time()
    success = await ejecutar_upload()
    fin = time.time()

    duracion = fin - inicio

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡UPLOAD COMPLETADO EXITOSAMENTE!")
        print(f"\n⏱️  Duración: {duracion:.1f} segundos")
        print("\n🎯 VIDEO PUBLICADO EN INSTAGRAM")
    else:
        print("⚠️  EJECUCIÓN CON ERRORES")
        print(f"\n⏱️  Duración: {duracion:.1f} segundos")
        print("\n🔧 POSIBLES SOLUCIONES:")
        print("   1. Verifica código 2FA (expira en 30s)")
        print("   2. Revisa credenciales")
        print("   3. Intenta login manual primero")

    print(f"\n⏰ Fin: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())