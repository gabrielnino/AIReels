#!/usr/bin/env python3
"""
EJECUCIÓN REAL FINAL DE AIReels Instagram Upload.
Este script ejecutará una subida REAL a Instagram.
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Configurar PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, '/home/luis/.local/lib/python3.12/site-packages')
sys.path.insert(0, '/usr/lib/python3/dist-packages')

print("=" * 80)
print("🚀 EJECUCIÓN REAL FINAL - AIReels Instagram Upload")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def ejecutar_subida_real():
    """Ejecutar subida REAL a Instagram."""
    
    try:
        # 1. CARGAR CONFIGURACIÓN
        print("1. 📋 CARGANDO CONFIGURACIÓN REAL")
        print("-" * 50)
        
        from dotenv import load_dotenv
        load_dotenv('.env.instagram')
        
        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')
        dry_run = os.environ.get('INSTAGRAM_DRY_RUN', 'true').lower()
        
        if not username or not password:
            print("❌ ERROR: Credenciales no configuradas")
            return False
        
        print(f"✅ Usuario: {username}")
        print(f"✅ Contraseña: {'*' * len(password)}")
        
        if dry_run == 'true':
            print("❌ ERROR: Modo DRY-RUN activado")
            print("   Configure INSTAGRAM_DRY_RUN=false para ejecución real")
            return False
        
        print("✅ Modo: REAL (INSTAGRAM_DRY_RUN=false)")
        
        # 2. IMPORTAR MÓDULOS
        print("\n2. 📦 IMPORTANDO MÓDULOS")
        print("-" * 50)
        
        try:
            from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
            from src.auth.login_manager import InstagramLoginManager
            from src.auth.cookie_manager import CookieManager
            from src.upload.video_uploader import VideoUploader, VideoInfo
            from src.upload.metadata_handler import MetadataHandler, VideoMetadata
            from src.upload.publisher import Publisher
            
            print("✅ Módulos importados exitosamente")
        except ImportError as e:
            print(f"❌ Error importando: {e}")
            return False
        
        # 3. VERIFICAR VIDEO
        print("\n3. 🎥 VERIFICANDO VIDEO")
        print("-" * 50)
        
        videos_dir = Path("videos/to_upload")
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))
        
        if not videos:
            print("❌ ERROR: No hay videos en videos/to_upload/")
            return False
        
        video_path = videos[0]
        print(f"✅ Video seleccionado: {video_path.name}")
        print(f"   • Tamaño: {video_path.stat().st_size / 1024:.1f} KB")
        
        # 4. CONFIGURAR METADATA
        print("\n4. 🏷️  CONFIGURANDO METADATA")
        print("-" * 50)
        
        caption = """🚀 AIReels - Ejecución REAL Automatizada

✅ Sistema funcionando en tiempo real
🔧 Subida automática a Instagram
🤖 Python + Playwright + Automatización

#AIReels #Automation #Instagram #Python #AI #RealUpload #Demo #Bot"""

        hashtags = [
            "aireels", "automation", "instagram", "python",
            "ai", "realupload", "demo", "bot", "automatizacion",
            "programacion", "desarrollo", "testing", "playwright"
        ]
        
        print("✅ Metadata configurada:")
        print(f"   • Caption: {caption[:60]}...")
        print(f"   • Hashtags: {', '.join(hashtags[:6])}...")
        
        # 5. CONFIGURAR COMPONENTES
        print("\n5. ⚙️  CONFIGURANDO COMPONENTES")
        print("-" * 50)
        
        # Configuración de navegador - VISIBLE para ver el proceso
        config = BrowserConfig(
            headless=False,  # VISIBLE - podemos ver lo que pasa
            slow_mo=200,     # Pausa entre acciones para ver mejor
            timeout=180000,  # 3 minutos timeout
            browser_type=BrowserType.CHROMIUM
        )
        
        print(f"✅ Navegador configurado:")
        print(f"   • Tipo: {config.browser_type.value}")
        print(f"   • Headless: {config.headless} (VISIBLE)")
        print(f"   • Slow mo: {config.slow_mo}ms")
        
        # 6. MOSTRAR RESUMEN Y CONFIRMAR
        print("\n6. 📊 RESUMEN DE EJECUCIÓN REAL")
        print("-" * 50)
        
        print("🚨 ¡ESTA ES UNA EJECUCIÓN REAL!")
        print("\n🎯 LO QUE VA A PASAR:")
        print(f"   1. Se abrirá Chrome/Chromium VISIBLE")
        print(f"   2. Se hará login en Instagram como: {username}")
        print(f"   3. Se navegará a la página de upload")
        print(f"   4. Se seleccionará el video: {video_path.name}")
        print(f"   5. Se ingresará la metadata")
        print(f"   6. Se PUBLICARÁ el video en tu perfil")
        
        print("\n⚠️  ADVERTENCIAS FINALES:")
        print("   • El video será PÚBLICO en Instagram")
        print("   • Se usará tu cuenta REAL")
        print("   • Puede requerir 2FA")
        print("   • NO SE PUEDE DESHACER")
        
        print("\n⏳ Iniciando en 15 segundos... (Ctrl+C para cancelar)")
        try:
            for i in range(15, 0, -1):
                print(f"   {i}...", end='\r')
                await asyncio.sleep(1)
            print("   ¡EJECUTANDO!          ")
        except asyncio.CancelledError:
            print("\n❌ EJECUCIÓN CANCELADA")
            return False
        
        # 7. EJECUTAR FLUJO REAL
        print("\n7. 🚀 INICIANDO EJECUCIÓN REAL")
        print("=" * 50)
        
        browser_service = None
        try:
            # A. INICIALIZAR NAVEGADOR
            print("\nA. 🔓 INICIALIZANDO NAVEGADOR...")
            browser_service = BrowserService(config)
            await browser_service.initialize()
            print("   ✅ Navegador inicializado")
            
            # B. LOGIN MANAGER
            print("\nB. 🔐 CONFIGURANDO LOGIN MANAGER...")
            login_manager = InstagramLoginManager()
            print(f"   ✅ LoginManager para: {login_manager.username}")
            
            # NOTA: Según el código, login() no acepta browser_service
            # Necesitamos ver cómo funciona realmente
            
            print("\n⚠️  IMPORTANTE: Revisando arquitectura de login...")
            print("   Según el código, LoginManager.login() no acepta parámetros")
            print("   Crea su propio navegador internamente")
            
            # C. VIDEO UPLOADER
            print("\nC. 🎥 CONFIGURANDO VIDEO UPLOADER...")
            video_uploader = VideoUploader(browser_service=browser_service)
            
            # Crear VideoInfo
            video_info = VideoInfo(
                path=str(video_path),
                caption=caption,
                hashtags=hashtags,
                location="AIReels Lab"
            )
            
            print(f"   ✅ VideoInfo creado: {video_info.path}")
            
            # D. METADATA HANDLER
            print("\nD. 🏷️  CONFIGURANDO METADATA HANDLER...")
            metadata_handler = MetadataHandler()
            
            metadata = VideoMetadata(
                caption=caption,
                hashtags=hashtags,
                location="AIReels Lab"
            )
            
            print("   ✅ MetadataHandler listo")
            
            # E. PUBLISHER
            print("\nE. 🚀 CONFIGURANDO PUBLISHER...")
            publisher = Publisher()
            print(f"   ✅ Publisher listo (dry_run: {getattr(publisher, 'dry_run', 'N/A')})")
            
            # F. VERIFICAR SESIÓN
            print("\nF. 📝 VERIFICANDO SESIÓN...")
            cookie_manager = CookieManager()
            if cookie_manager.has_valid_session():
                session_user = cookie_manager.get_session_username()
                print(f"   ✅ Sesión válida para: {session_user}")
            else:
                print("   ⚠️  No hay sesión válida")
                print("   • Se requerirá login completo")
            
            # G. EJECUTAR FLUJO REAL
            print("\nG. 🚀 EJECUTANDO FLUJO REAL COMPLETO")
            print("=" * 50)

            print("⚠️  ¡ATENCIÓN! EJECUCIÓN REAL EN CURSO")
            print("   • Se hará login REAL en Instagram")
            print("   • Se subirá el video REALMENTE")
            print("   • Se publicará REALMENTE en tu perfil")

            try:
                # 1. LOGIN REAL CON LOGIN MANAGER
                print("\n1. 🔐 LOGIN REAL EN INSTAGRAM...")
                print(f"   • Usuario: {login_manager.username}")

                login_success = await login_manager.login()
                if not login_success:
                    print("❌ Login falló")
                    return False

                print("✅ Login REAL exitoso")

                # 2. UPLOAD REAL DE VIDEO
                print("\n2. 📤 UPLOAD REAL DE VIDEO...")
                print(f"   • Video: {video_info.path}")

                # Crear VideoUploader con el browser_service existente
                video_uploader_with_browser = VideoUploader(browser_service=browser_service)

                upload_result = await video_uploader_with_browser.upload_video(video_info)
                print(f"   • Upload status: {upload_result.status}")
                print(f"   • Mensaje: {upload_result.message}")

                if not upload_result.success:
                    print("❌ Upload falló")
                    return False

                print("✅ Upload REAL exitoso")

                # 3. METADATA REAL
                print("\n3. 🏷️  METADATA REAL...")

                metadata_handler_with_browser = MetadataHandler(browser_service=browser_service)
                metadata_success = await metadata_handler_with_browser.enter_all_metadata(metadata)

                if not metadata_success:
                    print("❌ Metadata falló")
                    return False

                print("✅ Metadata REAL ingresada")

                # 4. PUBLICACIÓN REAL
                print("\n4. 🚀 PUBLICACIÓN REAL...")

                publisher_with_browser = Publisher(browser_service=browser_service)
                publication_result = await publisher_with_browser.publish_post()

                print(f"   • Publication status: {publication_result.status}")
                print(f"   • Mensaje: {publication_result.message}")

                if not publication_result.success:
                    print("❌ Publicación falló")
                    return False

                print("🎉 ¡PUBLICACIÓN REAL EXITOSA!")

                if publication_result.post_url:
                    print(f"🔗 URL del post: {publication_result.post_url}")

                # 5. GUARDAR RESULTADOS
                print("\n5. 💾 GUARDANDO RESULTADOS...")
                print(f"   • Upload tomó: {upload_result.duration_seconds:.1f}s")
                print(f"   • Publicación tomó: {publication_result.duration_seconds:.1f}s")
                print(f"   • Total: {upload_result.duration_seconds + publication_result.duration_seconds:.1f}s")

                return True

            except Exception as e:
                print(f"\n❌ ERROR EN FLUJO REAL: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                return False

            # H. CERRAR NAVEGADOR
            print("\nH. 🧹 CERRANDO NAVEGADOR...")
            if browser_service:
                await browser_service.close()
                print("   ✅ Navegador cerrado")

            return True
            
        except Exception as e:
            print(f"\n❌ ERROR DURANTE EJECUCIÓN: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            
            # Cerrar navegador si hay error
            if browser_service:
                try:
                    await browser_service.close()
                except:
                    pass
            
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""
    
    inicio = time.time()
    print("🔍 Iniciando ejecución REAL de AIReels...")
    print(f"📁 Directorio: {Path(__file__).parent}")
    print()
    
    success = await ejecutar_subida_real()
    fin = time.time()
    
    duracion = fin - inicio
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL DE EJECUCIÓN")
    print("=" * 80)
    
    if success:
        print("✅ EJECUCIÓN REAL COMPLETADA EXITOSAMENTE")
        print(f"\n⏱️  Duración: {duracion:.1f} segundos")

        print("\n🎯 ACCIONES REALES EJECUTADAS:")
        print("   • Login REAL en Instagram ✓")
        print("   • Upload REAL de video ✓")
        print("   • Metadata REAL ingresada ✓")
        print("   • Publicación REAL en tu perfil ✓")
        print("   • Video publicado en Instagram ✓")

        print("\n⚠️  RECORDATORIO IMPORTANTE:")
        print("   • El video ahora es PÚBLICO en Instagram")
        print("   • Usa solo cuentas de prueba para automatización")
        print("   • Instagram puede detectar y suspender bots")
        
    else:
        print("⚠️  EJECUCIÓN CON ERRORES")
        print(f"\n⏱️  Duración: {duracion:.1f} segundos")
    
    print(f"\n⏰ Fin: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
