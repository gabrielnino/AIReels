#!/usr/bin/env python3
"""
CONTINUAR UPLOAD DESDE 2FA

Este script asume que:
1. El navegador ya está abierto en Instagram
2. El usuario YA INGRESÓ MANUALMENTE el código 2FA
3. Instagram está mostrando "Trust this device"
4. Necesita hacer click en "Trust this device" y continuar con upload

🚨 El navegador debe estar ABIERTO Y VISIBLE
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
print("🚀 CONTINUAR UPLOAD DESDE 2FA - 'Trust this device'")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def continuar_desde_2fa():
    """Continuar desde punto donde usuario ya ingresó código 2FA."""

    print("🎯 OBJETIVO: Clickear 'Trust this device' y subir video")
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
        env_path = current_dir / "instagram-upload" / ".env.instagram"
        load_dotenv(str(env_path))

        username = os.environ.get('INSTAGRAM_USERNAME')
        print(f"✅ Usuario: {username}")

        # Verificar video
        videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

        if not videos:
            print("❌ No hay videos disponibles")
            return False

        video_path = videos[0]
        print(f"✅ Video: {video_path.name}")

        # Configurar navegador - CONECTARSE AL EXISTENTE
        print("\n🔗 CONECTANDO A NAVEGADOR EXISTENTE...")
        print("⚠️  Asegúrate que el navegador de Instagram esté ABIERTO")
        print("   y mostrando 'Trust this device'")

        config = BrowserConfig(
            headless=False,
            slow_mo=200,
            timeout=120000,
            browser_type=BrowserType.CHROMIUM
        )

        # Crear browser service (se conectará al navegador existente si es posible)
        browser_service = BrowserService(config)

        try:
            # Intentar conectar al navegador existente
            print("\n🔌 Intentando conectar al navegador Chrome/Chromium existente...")
            await browser_service.initialize(connect_to_existing=True)

            print("✅ Conectado al navegador existente")

            # Obtener la página actual
            pages = await browser_service.context.pages()
            if not pages:
                print("❌ No hay páginas abiertas en el navegador")
                return False

            page = pages[0]
            current_url = page.url
            print(f"📄 Página actual: {current_url}")

            # 1. BUSCAR Y HACER CLICK EN "TRUST THIS DEVICE"
            print("\n1. 🔍 BUSCANDO 'TRUST THIS DEVICE'...")

            trust_device_selectors = [
                'button:has-text("Trust this device")',
                'button:has-text("trust this device")',
                'button:has-text("Trust Device")',
                'button:has-text("trust device")',
                'button:has-text("Remember this device")',
                'button:has-text("remember this device")',
                'button:has-text("Save this device")',
                'button:has-text("save this device")',
                'div[role="button"]:has-text("Trust this device")',
                'div[role="button"]:has-text("Save this device")',
                'input[type="checkbox"][name="trust"]',
                'input[type="checkbox"][name="remember"]',
                'input[type="checkbox"][name="save"]'
            ]

            trust_found = False
            for selector in trust_device_selectors:
                try:
                    trust_element = page.locator(selector).first
                    if await trust_element.is_visible(timeout=3000):
                        print(f"✅ 'Trust this device' encontrado: {selector}")
                        await trust_element.click()
                        print("✅ Click en 'Trust this device'")
                        trust_found = True
                        await asyncio.sleep(2)
                        break
                except:
                    continue

            if not trust_found:
                print("⚠️  'Trust this device' no encontrado")
                print("   Continuando de todos modos...")

            # 2. ESPERAR LOGIN COMPLETO
            print("\n2. ⏳ ESPERANDO LOGIN COMPLETO...")

            try:
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=15000)
                print("✅ Login completado - en página principal de Instagram")
            except:
                print("⚠️  No se pudo verificar login completo")
                print("   Continuando de todos modos...")

            # 3. PREPARAR UPLOAD
            print("\n3. 🎥 PREPARANDO UPLOAD...")

            caption = """🚀 AIReels - Upload Automatizado

✅ Login con 2FA exitoso
🔧 Continuación automática después de 'Trust this device'
🤖 Sistema funcionando correctamente

#AIReels #Automation #Instagram #Python #AI #Upload #TrustThisDevice"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "trustthisdevice", "demo", "bot",
                "automatizacion", "programacion", "testing"
            ]

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

            # 4. UPLOAD DE VIDEO
            print("\n4. 📤 SUBIENDO VIDEO...")
            print(f"   • Video: {video_path.name}")

            upload_result = await video_uploader.upload_video(video_info)

            print(f"   • Status: {upload_result.status}")
            print(f"   • Mensaje: {upload_result.message}")

            if not upload_result.success:
                print("❌ Upload falló")
                return False

            print("✅ Upload exitoso")

            # 5. METADATA
            print("\n5. 🏷️  METADATA...")

            metadata_success = await metadata_handler.enter_all_metadata(metadata)

            if not metadata_success:
                print("❌ Metadata falló")
                return False

            print("✅ Metadata ingresada")

            # 6. PUBLICACIÓN
            print("\n6. 🚀 PUBLICANDO...")
            print("⚠️  ¡ÚLTIMA ACCIÓN - VIDEO SE PUBLICARÁ!")

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
            # NO cerrar el navegador - dejarlo abierto
            print("\n⚠️  Navegador dejado ABIERTO")
            # await browser_service.close()

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

    print("⚠️  INSTRUCCIONES IMPORTANTES:")
    print("1. El navegador de Instagram debe estar ABIERTO")
    print("2. Debe mostrar 'Trust this device' (después de ingresar 2FA)")
    print("3. NO cierres el navegador")
    print()

    print("⏳ Iniciando en 5 segundos...")
    for i in range(5, 0, -1):
        print(f"   {i}...", end='\r')
        await asyncio.sleep(1)
    print("   🚀 INICIANDO...          ")

    success = await continuar_desde_2fa()

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡UPLOAD COMPLETADO!")
        print("🎉 Video publicado en Instagram")
    else:
        print("⚠️  EJECUCIÓN FALLÓ")
        print("\n🔧 POSIBLES RAZONES:")
        print("   1. Navegador no está abierto")
        print("   2. 'Trust this device' no visible")
        print("   3. Instagram cerró sesión")
        print("   4. Problemas de conexión")

    return success

if __name__ == "__main__":
    asyncio.run(main())