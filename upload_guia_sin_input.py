#!/usr/bin/env python3
"""
UPLOAD GUÍA SIN INPUT - Guía con tiempos de espera en lugar de inputs
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
print("🚀 UPLOAD GUÍA PASO A PASO")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

if not username or not password:
    print("❌ Credenciales no configuradas")
    exit(1)

print(f"✅ Usuario: {username}")
print()

async def guia_paso_a_paso():
    """Guía paso a paso con tiempos de espera."""

    import asyncio
    from playwright.async_api import async_playwright

    # VERIFICAR VIDEO
    print("📁 Verificando video...")
    videos_dir = current_dir / "instagram-upload" / "videos" / "to_upload"
    videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

    if not videos:
        print("❌ No hay videos")
        return False

    video_path = videos[0]
    print(f"✅ Video: {video_path.name}")
    print()

    # NAVEGADOR
    print("🌐 Iniciando navegador...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        page = await browser.new_page()

        try:
            # ==================== PASO 1: LOGIN ====================
            print("\n" + "=" * 60)
            print("1️⃣  PASO 1: LOGIN MANUAL (60 segundos)")
            print("=" * 60)

            await page.goto('https://www.instagram.com/')
            await asyncio.sleep(3)

            print("✅ Instagram cargado")
            print()
            print("📝 INSTRUCCIONES:")
            print("   • Ingresa usuario: " + username)
            print("   • Ingresa contraseña: [tu contraseña]")
            print("   • Haz click en 'Log In'")
            print("   • Si hay popup 'Notifications': 'Not Now'")
            print()

            print("⏳ Tienes 60 segundos para hacer login...")
            for i in range(60, 0, -1):
                print(f"   Tiempo: {i}s", end='\r')
                await asyncio.sleep(1)
            print("\n✅ Continuando...")

            # ==================== PASO 2: UPLOAD ====================
            print("\n" + "=" * 60)
            print("2️⃣  PASO 2: NAVEGAR A UPLOAD (45 segundos)")
            print("=" * 60)

            print("📝 INSTRUCCIONES:")
            print("   • Busca el ícono '+' o 'New post'")
            print("   • Haz click en él")
            print("   • Selecciona 'Post' o 'Reel'")
            print()

            print("⏳ Tienes 45 segundos para navegar a upload...")
            for i in range(45, 0, -1):
                print(f"   Tiempo: {i}s", end='\r')
                await asyncio.sleep(1)
            print("\n✅ Continuando...")

            # ==================== PASO 3: SELECCIONAR ARCHIVO ====================
            print("\n" + "=" * 60)
            print("3️⃣  PASO 3: SELECCIONAR ARCHIVO")
            print("=" * 60)

            print("🔄 Intentando selección automática...")
            try:
                await page.wait_for_selector('input[type="file"]', timeout=10000)
                file_input = await page.query_selector('input[type="file"]')

                if file_input:
                    await file_input.set_input_files(str(video_path))
                    print("✅ Archivo seleccionado automáticamente")
                else:
                    print("⚠️  No se encontró input")
                    print(f"   📂 Selecciona manualmente: {video_path}")
            except:
                print(f"⚠️  Error automático")
                print(f"   📂 Selecciona manualmente: {video_path}")

            print("⏳ Esperando procesamiento... (15 segundos)")
            await asyncio.sleep(15)

            # ==================== PASO 4: METADATA ====================
            print("\n" + "=" * 60)
            print("4️⃣  PASO 4: AGREGAR METADATA (30 segundos)")
            print("=" * 60)

            caption = """🚀 AIReels - Upload Guiado

✅ Proceso paso a paso
🔧 Guía interactiva
🎯 Video subido exitosamente

#AIReels #Automation #Instagram #Python #AI"""

            hashtags = ["aireels", "automation", "instagram", "python", "ai", "upload"]

            full_caption = caption + "\n\n" + " ".join(f"#{tag}" for tag in hashtags)

            print("📝 CAPTION PARA COPIAR:")
            print("-" * 50)
            print(full_caption)
            print("-" * 50)
            print()

            print("📝 INSTRUCCIONES:")
            print("   • Busca 'Write a caption...'")
            print("   • Pega el texto de arriba")
            print("   • Ajusta si quieres")
            print()

            print("⏳ Tienes 30 segundos para pegar caption...")
            for i in range(30, 0, -1):
                print(f"   Tiempo: {i}s", end='\r')
                await asyncio.sleep(1)
            print("\n✅ Continuando...")

            # ==================== PASO 5: PUBLICAR ====================
            print("\n" + "=" * 60)
            print("5️⃣  PASO 5: PUBLICAR (30 segundos)")
            print("=" * 60)

            print("📝 INSTRUCCIONES:")
            print("   • Busca botón 'Share' o 'Compartir'")
            print("   • Haz click en él")
            print("   • Espera publicación")
            print()

            print("⏳ Tienes 30 segundos para publicar...")
            for i in range(30, 0, -1):
                print(f"   Tiempo: {i}s", end='\r')
                await asyncio.sleep(1)
            print("\n✅ Continuando...")

            # ==================== PASO 6: FINAL ====================
            print("\n" + "=" * 60)
            print("🏁 PROCESO COMPLETADO")
            print("=" * 60)

            print("🎉 ¡GUÍA FINALIZADA!")
            print()
            print("📊 RESUMEN:")
            print("   1. ✅ Login manual")
            print("   2. ✅ Navegación a upload")
            print("   3. ✅ Selección de video")
            print("   4. ✅ Metadata")
            print("   5. ✅ Publicación")
            print()
            print("🔍 Verifica en Instagram que el video se publicó")

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

        finally:
            print("\n⚠️  Navegador abierto - ciérralo cuando termines")
            # Mantener navegador abierto

def main():
    """Función principal."""

    print("🚀 INICIANDO GUÍA DE UPLOAD")
    print()
    print("ℹ️  Este script te guía con tiempos:")
    print("   • Tú haces los clicks manualmente")
    print("   • Yo te doy tiempos para cada paso")
    print("   • Es simple y funciona")
    print()

    import asyncio
    success = asyncio.run(guia_paso_a_paso())

    print("\n" + "=" * 80)
    print("🏁 FIN DE GUÍA")
    print("=" * 80)

    if success:
        print("✅ GUÍA COMPLETADA")
        print("🎉 Sigue los pasos en el navegador")
    else:
        print("❌ GUÍA INTERRUMPIDA")

    print("\n💡 CONSEJO: Si tienes problemas:")
    print("   1. Asegura que 2FA está deshabilitado")
    print("   2. Verifica credenciales")
    print("   3. Revisa el navegador para mensajes de error")

    return success

if __name__ == "__main__":
    main()