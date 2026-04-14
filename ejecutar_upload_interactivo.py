#!/usr/bin/env python3
"""
EJECUTAR UPLOAD INTERACTIVO - Guía paso a paso completa

Este script guía al usuario a través de todo el proceso:
1. Abre navegador
2. Usuario hace login MANUAL
3. Usuario cierra popups MANUAL
4. Usuario navega a upload MANUAL
5. Script ayuda con selección de archivo
6. Script ayuda con metadata
7. Script ayuda con publicación
"""

import os
import time
import sys
from pathlib import Path

# Cargar configuración
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "instagram-upload"))

from dotenv import load_dotenv
env_path = current_dir / "instagram-upload" / ".env.instagram"
load_dotenv(str(env_path))

username = os.environ.get('INSTAGRAM_USERNAME')
password = os.environ.get('INSTAGRAM_PASSWORD')

print("=" * 80)
print("🚀 EJECUTAR UPLOAD INTERACTIVO")
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

async def ejecutar_paso_a_paso():
    """Ejecutar proceso paso a paso con guía interactiva."""

    import asyncio
    from playwright.async_api import async_playwright

    print("🎯 MODO INTERACTIVO - Te guiaré paso a paso")
    print()

    # PASO 0: VERIFICAR VIDEO
    print("📁 Verificando video...")
    videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
    videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

    if not videos:
        print("❌ No hay videos en instagram-upload/videos/to_upload/")
        print("   Coloca un video allí primero")
        return False

    video_path = videos[0]
    print(f"✅ Video encontrado: {video_path.name}")
    print(f"📏 Tamaño: {video_path.stat().st_size / (1024*1024):.1f} MB")
    print()

    # INICIAR NAVEGADOR
    print("🌐 Iniciando navegador...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        page = await browser.new_page()

        try:
            # ============================================
            # PASO 1: LOGIN MANUAL
            # ============================================
            print("\n" + "=" * 60)
            print("🖱️  PASO 1: LOGIN MANUAL EN INSTAGRAM")
            print("=" * 60)

            await page.goto('https://www.instagram.com/')
            await asyncio.sleep(3)

            print("✅ Instagram cargado")
            print()
            print("📝 INSTRUCCIONES:")
            print("   1. En el navegador, ingresa usuario y contraseña")
            print("   2. Haz click en 'Log In'")
            print("   3. Si pide 2FA, usa código si está deshabilitado debería pasar")
            print("   4. Espera a que cargue la página principal")
            print()

            input("👤 Presiona ENTER cuando hayas completado el login... ")
            print("✅ Login completado")

            # ============================================
            # PASO 2: MANEJAR POPUP DE NOTIFICACIONES
            # ============================================
            print("\n" + "=" * 60)
            print("🔔 PASO 2: MANEJAR POPUP DE NOTIFICACIONES")
            print("=" * 60)

            print("📝 INSTRUCCIONES:")
            print("   Si aparece popup 'Turn on Notifications':")
            print("   1. Haz click en 'Not Now'")
            print("   2. Si no aparece, continúa")
            print()

            input("👁️  Presiona ENTER después de manejar popups... ")
            print("✅ Popups manejados")

            # ============================================
            # PASO 3: NAVEGAR A UPLOAD
            # ============================================
            print("\n" + "=" * 60)
            print("📍 PASO 3: NAVEGAR A SUBIR VIDEO")
            print("=" * 60)

            print("📝 INSTRUCCIONES:")
            print("   En Instagram (en el navegador):")
            print("   1. Busca el ícono '+' o 'New post'")
            print("   2. Haz click en él")
            print("   3. Selecciona 'Post' o 'Reel'")
            print("   4. Debería abrirse ventana de selección de archivo")
            print()

            input("📤 Presiona ENTER cuando estés en la pantalla de upload... ")
            print("✅ En pantalla de upload")

            # ============================================
            # PASO 4: SELECCIONAR ARCHIVO
            # ============================================
            print("\n" + "=" * 60)
            print("📁 PASO 4: SELECCIONAR ARCHIVO (AYUDA AUTOMÁTICA)")
            print("=" * 60)

            print(f"📂 Intentando seleccionar archivo automáticamente: {video_path.name}")

            # Esperar a que aparezca input de archivo
            try:
                await page.wait_for_selector('input[type="file"]', timeout=10000)
                file_input = await page.query_selector('input[type="file"]')

                if file_input:
                    await file_input.set_input_files(str(video_path))
                    print("✅ Archivo seleccionado automáticamente")
                    await asyncio.sleep(5)
                else:
                    print("⚠️  No se encontró input de archivo")
                    print("   Selecciona el archivo MANUALMENTE:")
                    print(f"   Ruta: {video_path}")
            except Exception as e:
                print(f"⚠️  Error seleccionando archivo automáticamente: {e}")
                print("   Selecciona el archivo MANUALMENTE:")
                print(f"   Ruta: {video_path}")

            print("\n⏳ Esperando procesamiento del video...")
            await asyncio.sleep(10)

            input("✅ Presiona ENTER cuando el video haya cargado... ")

            # ============================================
            # PASO 5: METADATA (AYUDA)
            # ============================================
            print("\n" + "=" * 60)
            print("🏷️  PASO 5: METADATA (TEXTO PREPARADO)")
            print("=" * 60)

            caption = """🚀 AIReels - Upload Interactivo Guiado

✅ Login manual exitoso
🔧 Proceso paso a paso
🎯 Video subido con éxito
🤖 Asistencia automatizada

#AIReels #Automation #Instagram #Python #AI #Upload #Interactive #Guide"""

            hashtags = [
                "aireels", "automation", "instagram", "python",
                "ai", "upload", "interactive", "guide", "success"
            ]

            full_caption = caption + "\n\n" + " ".join(f"#{tag}" for tag in hashtags)

            print("📝 CAPTION PREPARADO (copia y pega):")
            print("-" * 50)
            print(full_caption)
            print("-" * 50)
            print()

            print("📝 INSTRUCCIONES:")
            print("   1. Busca el campo 'Write a caption...'")
            print("   2. Pega el texto de arriba")
            print("   3. Ajusta si lo deseas")
            print()

            input("📝 Presiona ENTER después de pegar el caption... ")

            # ============================================
            # PASO 6: PUBLICAR
            # ============================================
            print("\n" + "=" * 60)
            print("🚀 PASO 6: PUBLICAR")
            print("=" * 60)

            print("📝 INSTRUCCIONES:")
            print("   1. Busca el botón 'Share' o 'Compartir'")
            print("   2. Haz click en él")
            print("   3. Espera a que se complete la publicación")
            print("   4. Verifica que el video se publicó")
            print()

            input("🎉 Presiona ENTER después de publicar... ")

            # ============================================
            # PASO 7: VERIFICACIÓN
            # ============================================
            print("\n" + "=" * 60)
            print("✅ PASO 7: VERIFICACIÓN FINAL")
            print("=" * 60)

            print("🎉 ¡PROCESO COMPLETADO!")
            print()
            print("📊 RESUMEN:")
            print("   1. ✅ Login manual completado")
            print("   2. ✅ Popups manejados")
            print("   3. ✅ Navegación a upload")
            print("   4. ✅ Video seleccionado")
            print("   5. ✅ Metadata agregada")
            print("   6. ✅ Video publicado")
            print()
            print("🔍 Verifica en Instagram que el video se publicó correctamente")

            return True

        except Exception as e:
            print(f"❌ Error durante el proceso: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            print("\n⚠️  Navegador mantenido abierto")
            print("   Cierra el navegador cuando hayas terminado de verificar")

def main():
    """Función principal."""

    print("🚀 INICIANDO UPLOAD INTERACTIVO")
    print()
    print("ℹ️  Este modo es 100% interactivo:")
    print("   • Tú controlas el navegador")
    print("   • Yo te guío paso a paso")
    print("   • Es más confiable que automático")
    print()

    import asyncio
    success = asyncio.run(ejecutar_paso_a_paso())

    print("\n" + "=" * 80)
    print("🏁 FIN DE EJECUCIÓN")
    print("=" * 80)

    if success:
        print("✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print("🎉 Has subido un video a Instagram")
        print("\n📚 APRENDIZAJE:")
        print("   Ahora sabes el proceso completo")
        print("   Puedes repetirlo o automatizar partes")
    else:
        print("❌ PROCESO INTERRUMPIDO")
        print("\n🔧 PRÓXIMOS PASOS:")
        print("   1. Revisa qué paso falló")
        print("   2. Intenta manualmente sin script")
        print("   3. Toma notas de los problemas")
        print("   4. Pide ayuda con los errores específicos")

    return success

if __name__ == "__main__":
    main()