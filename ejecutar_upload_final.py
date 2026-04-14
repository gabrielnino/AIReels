#!/usr/bin/env python3
"""
EJECUTAR UPLOAD FINAL A INSTAGRAM

🚨 INSTRUCCIONES IMPORTANTES:
1. NECESITAS UN CÓDIGO 2FA FRESCO (cambia cada 30 segundos)
2. Abre tu app de autenticación (Google Authenticator, Authy, etc.)
3. Busca 'Instagram' o 'fiestacotoday'
4. Copia el código de 6 dígitos que aparece AHORA MISMO
5. El código 688774 ya EXPIRÓ si fue generado hace más de 30 segundos
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
print("🚀 UPLOAD FINAL A INSTAGRAM - CÓDIGO 2FA FRESCO REQUERIDO")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def ejecutar_upload():
    """Ejecutar upload con código 2FA fresco."""

    print("🎯 OBJETIVO: Subir video REAL a Instagram")
    print()

    # Información CRÍTICA sobre 2FA
    print("⚠️  ⚠️  ⚠️  ATENCIÓN CRÍTICA SOBRE 2FA ⚠️  ⚠️  ⚠️")
    print("-" * 60)
    print("📱 Instagram requiere autenticación de dos factores (2FA)")
    print("🔢 Los códigos 2FA CAMBIAN CADA 30 SEGUNDOS")
    print("🕒 El código 688774 YA EXPIRÓ si fue generado hace >30s")
    print()

    print("📱 PARA OBTENER UN CÓDIGO 2FA FRESCO:")
    print("   1. Abre tu app de autenticación (Google Authenticator, Authy, etc.)")
    print("   2. Busca 'Instagram' o 'fiestacotoday'")
    print("   3. Copia el código de 6 dígitos que aparece AHORA MISMO")
    print("   4. El código es VÁLIDO por solo 30 segundos")
    print()

    # Obtener código 2FA fresco del usuario
    print("🔢 INGRESA EL CÓDIGO 2FA FRESCO DE 6 DÍGITOS:")

    # Nota: No podemos pedir input interactivo en este entorno
    # El usuario necesita actualizar manualmente el archivo .env.instagram
    env_path = current_dir / "instagram-upload" / ".env.instagram"

    print(f"\n💡 ACTUALIZA MANUALMENTE EL ARCHIVO:")
    print(f"   {env_path}")
    print("\n📝 Busca esta línea:")
    print("   INSTAGRAM_2FA_CODE=688774")
    print("\n✏️  Cámbiala por:")
    print("   INSTAGRAM_2FA_CODE=TU_CODIGO_FRESCO")
    print("\n🔢 Donde TU_CODIGO_FRESCO es el código de 6 dígitos de AHORA")
    print()

    # Leer código actual del archivo
    try:
        with open(env_path, 'r') as f:
            contenido = f.read()
            if "INSTAGRAM_2FA_CODE=" in contenido:
                # Extraer código actual
                for linea in contenido.split('\n'):
                    if linea.startswith('INSTAGRAM_2FA_CODE='):
                        codigo_actual = linea.split('=')[1]
                        print(f"📄 Código 2FA actual en archivo: {codigo_actual}")
                        if codigo_actual == "688774":
                            print("   ⚠️  Este código probablemente ya EXPIRÓ")
                        break
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

    print("\n⏳ Esperando 30 segundos para que actualices el archivo...")
    print("   (Presiona Ctrl+C si necesitas más tiempo)")
    try:
        for i in range(30, 0, -1):
            print(f"   {i} segundos restantes...", end='\r')
            await asyncio.sleep(1)
        print("   ✅ Continuando...          ")
    except asyncio.CancelledError:
        print("\n⏸️  Pausado. Actualiza el archivo y ejecuta de nuevo.")
        return False

    # Ahora ejecutar el flujo normal
    print("\n🔄 INICIANDO FLUJO DE UPLOAD...")
    print()

    try:
        # Importar módulos
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.auth.login_manager import InstagramLoginManager
        from src.upload.video_uploader import VideoUploader, VideoInfo
        from src.upload.metadata_handler import MetadataHandler, VideoMetadata
        from src.upload.publisher import Publisher

        print("✅ Módulos importados")

        # Cargar configuración
        from dotenv import load_dotenv
        load_dotenv(str(env_path))

        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')
        codigo_2fa = os.environ.get('INSTAGRAM_2FA_CODE')

        if not username or not password:
            print("❌ Credenciales no configuradas")
            return False

        print(f"✅ Usuario: {username}")
        print(f"✅ Código 2FA configurado: {codigo_2fa}")

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
            headless=False,
            slow_mo=200,
            timeout=120000,
            browser_type=BrowserType.CHROMIUM
        )

        print("✅ Navegador configurado (visible)")

        # Resumen final
        print("\n" + "=" * 60)
        print("🚨 RESUMEN - ACCIONES REALES")
        print("=" * 60)
        print(f"📋 LO QUE VA A PASAR:")
        print(f"   1. Login REAL: {username}")
        print(f"   2. Código 2FA: {codigo_2fa}")
        print(f"   3. Upload REAL: {video_path.name}")
        print(f"   4. Publicación REAL en Instagram")

        print("\n⏳ Iniciando en 5 segundos...")
        for i in range(5, 0, -1):
            print(f"   {i}...", end='\r')
            await asyncio.sleep(1)
        print("   🚀 EJECUTANDO...          ")

        # EJECUCIÓN
        browser_service = BrowserService(config)

        try:
            # Inicializar navegador
            await browser_service.initialize()
            print("✅ Navegador inicializado")

            # Login
            login_manager = InstagramLoginManager()
            print(f"🔐 Login con: {login_manager.username}")

            login_success = await login_manager.login()

            if not login_success:
                print("❌ Login falló")
                print("   Posibles causas:")
                print("   • Código 2FA expirado (¡cambia cada 30s!)")
                print("   • Credenciales incorrectas")
                print("   • Instagram bloqueó el acceso")
                return False

            print("✅ Login exitoso")

            # Upload
            video_info = VideoInfo(
                path=str(video_path),
                caption="🚀 AIReels - Upload Automatizado #AIReels #Automation",
                hashtags=["aireels", "automation", "instagram", "python", "ai"],
                location="AIReels Lab"
            )

            metadata = VideoMetadata(
                caption="🚀 AIReels - Upload Automatizado #AIReels #Automation",
                hashtags=["aireels", "automation", "instagram", "python", "ai"],
                location="AIReels Lab"
            )

            video_uploader = VideoUploader(browser_service=browser_service)
            metadata_handler = MetadataHandler(browser_service=browser_service)
            publisher = Publisher(browser_service=browser_service)

            print("📤 Subiendo video...")
            upload_result = await video_uploader.upload_video(video_info)

            if not upload_result.success:
                print("❌ Upload falló")
                return False

            print("✅ Upload exitoso")

            print("🏷️  Ingresando metadata...")
            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")

            print("🚀 Publicando...")
            publication_result = await publisher.publish_post()

            if not publication_result.success:
                print("❌ Publicación falló")
                return False

            print("🎉 ¡PUBLICACIÓN EXITOSA!")
            if publication_result.post_url:
                print(f"🔗 URL: {publication_result.post_url}")

            return True

        finally:
            await browser_service.close()
            print("✅ Navegador cerrado")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""

    print("⚠️  LEE LAS INSTRUCCIONES SOBRE 2FA ARRIBA ⚠️")
    print()

    success = await ejecutar_upload()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡UPLOAD COMPLETADO!")
        print("🎉 Video publicado en Instagram")
    else:
        print("⚠️  EJECUCIÓN FALLÓ")
        print("\n🔧 RAZONES COMUNES:")
        print("   1. Código 2FA expirado (¡CAMBIALO!)")
        print("   2. Credenciales incorrectas")
        print("   3. Instagram bloqueó el acceso")
        print("   4. Problemas de red/conexión")

    return success

if __name__ == "__main__":
    asyncio.run(main())