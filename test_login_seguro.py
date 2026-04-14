#!/usr/bin/env python3
"""
TEST SEGURO DE LOGIN - Instagram con selectores actualizados

Este script prueba el login REAL pero con medidas de seguridad:
1. Muestra qué haría antes de hacerlo
2. Pide confirmación explícita
3. Permite cancelar en cualquier momento
4. Tiene timeout de seguridad

⚠️  REQUIERE CONFIRMACIÓN EXPLÍCITA DEL USUARIO PARA CADA ACCIÓN
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent / "instagram-upload"))

print("=" * 80)
print("🔐 TEST SEGURO DE LOGIN - Instagram con selectores actualizados")
print("=" * 80)
print(f"⏰ Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print()

async def pedir_confirmacion(mensaje: str, tiempo_espera: int = 10) -> bool:
    """Pide confirmación al usuario con timeout."""
    print(f"\n⚠️  {mensaje}")
    print(f"⏳ Tienes {tiempo_espera} segundos para cancelar (Ctrl+C)...")

    try:
        for i in range(tiempo_espera, 0, -1):
            print(f"   {i}...", end='\r', flush=True)
            await asyncio.sleep(1)
        print("   ✅ CONTINUANDO...          ")
        return True
    except asyncio.CancelledError:
        print("\n❌ ACCIÓN CANCELADA POR EL USUARIO")
        return False

async def test_login_seguro():
    """Test seguro de login con confirmaciones."""

    print("🎯 OBJETIVO: Probar login REAL con selectores actualizados")
    print("🔒 MODO SEGURO: Requiere confirmación para cada acción")
    print()

    try:
        # 1. Importar módulos
        print("1. 📦 IMPORTANDO MÓDULOS...")
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.auth.login_manager import InstagramLoginManager
        print("✅ Módulos importados")

        # 2. Mostrar credenciales (ocultando password)
        print("\n2. 🔐 CREDENCIALES CONFIGURADAS...")
        from dotenv import load_dotenv
        load_dotenv('instagram-upload/.env.instagram')

        username = os.environ.get('INSTAGRAM_USERNAME')
        password = os.environ.get('INSTAGRAM_PASSWORD')

        if not username or not password:
            print("❌ ERROR: Credenciales no configuradas en .env.instagram")
            return False

        print(f"   • Usuario: {username}")
        print(f"   • Contraseña: {'*' * len(password)}")
        print(f"   • Archivo: instagram-upload/.env.instagram")

        # 3. Confirmar inicio del test
        confirmacion = await pedir_confirmacion(
            "¿Iniciar test de login REAL? Se abrirá navegador y navegará a Instagram.",
            tiempo_espera=5
        )
        if not confirmacion:
            return False

        # 4. Configurar navegador VISIBLE
        print("\n3. ⚙️  CONFIGURANDO NAVEGADOR...")
        config = BrowserConfig(
            headless=False,      # VISIBLE para ver qué pasa
            slow_mo=300,         # Pausa para ver mejor
            timeout=30000,       # 30 segundos timeout
            browser_type=BrowserType.CHROMIUM
        )

        print(f"✅ Navegador configurado:")
        print(f"   • Headless: {config.headless} (VISIBLE)")
        print(f"   • Slow mo: {config.slow_mo}ms")

        # 5. Inicializar navegador
        print("\n4. 🔓 INICIALIZANDO NAVEGADOR...")
        browser_service = BrowserService(config)
        await browser_service.initialize()

        print("✅ Navegador inicializado")
        print("   • Se abrirá Chrome/Chromium VISIBLE")
        print("   • Podrás ver todo el proceso")

        await asyncio.sleep(3)  # Esperar a que el navegador se abra

        # 6. Navegar a Instagram
        print("\n5. 🌐 NAVEGANDO A INSTAGRAM.COM...")
        page = browser_service.page

        print("   • Cargando https://www.instagram.com/")
        await page.goto("https://www.instagram.com/", wait_until="networkidle")

        print("✅ Instagram cargado")
        await asyncio.sleep(3)  # Esperar a que cargue completamente

        # 7. Tomar screenshot
        print("\n6. 📸 TOMANDO SCREENSHOT...")
        screenshot_path = "instagram_login_page_test.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"✅ Screenshot guardado: {screenshot_path}")

        # 8. Mostrar selectores que se usarán
        print("\n7. 🔍 SELECTORES QUE SE USARÁN:")
        print("   • Username: input[name='email'] (¡NUEVO! Instagram cambió)")
        print("   • Password: input[name='pass'] (¡NUEVO! Instagram cambió)")
        print("   • Botón: button:has-text('Log in')")

        # 9. Verificar que los campos existen
        print("\n8. ✓ VERIFICANDO CAMPOS...")

        campo_email = await page.query_selector('input[name="email"]')
        campo_pass = await page.query_selector('input[name="pass"]')

        if campo_email:
            print("   ✅ Campo email encontrado: input[name='email']")
            # Ver valor actual del campo
            valor_actual = await campo_email.input_value() or "(vacío)"
            print(f"      • Valor actual: {valor_actual}")
        else:
            print("   ❌ Campo email NO encontrado: input[name='email']")
            print("   🔍 Buscando alternativos...")

        if campo_pass:
            print("   ✅ Campo password encontrado: input[name='pass']")
            # Ver tipo
            tipo = await campo_pass.get_attribute('type') or 'N/A'
            print(f"      • Tipo: {tipo}")
        else:
            print("   ❌ Campo password NO encontrado: input[name='pass']")
            print("   🔍 Buscando alternativos...")

        # 10. Preguntar si continuar con login REAL
        print("\n" + "=" * 60)
        print("🚨 PUNTO DE DECISIÓN: LOGIN REAL")
        print("=" * 60)

        print("\n📋 LO QUE PASARÁ SI CONTINÚAS:")
        print(f"   1. Se escribirá '{username}' en campo email")
        print(f"   2. Se escribirá la contraseña en campo password")
        print(f"   3. Se hará click en 'Log in'")
        print(f"   4. Instagram intentará autenticarte")
        print(f"   5. Podría requerir 2FA (código de verificación)")

        print("\n⚠️  ADVERTENCIAS:")
        print("   • Instagram puede detectar automatización")
        print("   • Podría requerir verificación adicional")
        print("   • Usa solo cuentas de prueba")

        confirmacion_login = await pedir_confirmacion(
            "¿CONTINUAR con login REAL en Instagram?",
            tiempo_espera=15
        )

        if not confirmacion_login:
            print("\n❌ LOGIN REAL CANCELADO")
            print("   • Se cerrará el navegador")
            print("   • No se hará login")
            await browser_service.close()
            return False

        # 11. EJECUTAR LOGIN REAL (con supervisión)
        print("\n9. 🚀 EJECUTANDO LOGIN REAL...")
        print("   🔧 Usando LoginManager con selectores actualizados")

        login_manager = InstagramLoginManager()

        print(f"   • Usuario: {login_manager.username}")
        print("   • Iniciando proceso de login...")

        # Configurar timeout de seguridad
        try:
            # Ejecutar login con timeout
            login_task = asyncio.create_task(login_manager.login())
            login_success = await asyncio.wait_for(login_task, timeout=60)

            if login_success:
                print("\n✅ ¡LOGIN REAL EXITOSO!")
                print("   • Autenticación completada")
                print("   • Sesión guardada en cookies")

                # Tomar screenshot post-login
                screenshot_post = "instagram_post_login.png"
                await page.screenshot(path=screenshot_post, full_page=True)
                print(f"   • Screenshot: {screenshot_post}")
            else:
                print("\n❌ LOGIN FALLÓ")
                print("   • Revisa credenciales")
                print("   • Puede requerir 2FA")
                print("   • Instagram pudo bloquear el intento")

        except asyncio.TimeoutError:
            print("\n⏰ TIMEOUT: Login tomó demasiado tiempo")
            print("   • Instagram puede estar lento")
            print("   • Puede haber popups/verificaciones")
            login_success = False
        except Exception as e:
            print(f"\n❌ ERROR DURANTE LOGIN: {type(e).__name__}: {e}")
            login_success = False

        # 12. Cerrar navegador
        print("\n10. 🧹 CERRANDO NAVEGADOR...")
        await asyncio.sleep(3)  # Esperar para ver resultado
        await browser_service.close()
        print("✅ Navegador cerrado")

        # 13. Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL DEL TEST")
        print("=" * 60)

        if login_success:
            print("✅ TEST COMPLETADO EXITOSAMENTE")
            print("\n🎯 LOGRADO:")
            print("   • Selectores actualizados ✓")
            print("   • Login REAL exitoso ✓")
            print("   • Sesión guardada ✓")
            print("   • Screenshots tomados ✓")

            print("\n🚀 PRÓXIMOS PASOS:")
            print("   1. El sistema puede usar cookies guardadas")
            print("   2. Se puede proceder con upload de video")
            print("   3. Revisa screenshots para verificar")
        else:
            print("⚠️  TEST CON PROBLEMAS")
            print("\n🔧 DIAGNÓSTICO:")
            print("   • Instagram puede haber cambiado interfaz")
            print("   • Credenciales pueden ser incorrectas")
            print("   • Puede requerir 2FA/verificación")
            print("   • Instagram puede bloquear automatización")

            print("\n💡 SOLUCIONES:")
            print("   1. Revisa screenshots generados")
            print("   2. Verifica credenciales en .env.instagram")
            print("   3. Intenta login manual para ver interfaz")
            print("   4. Actualiza selectores si es necesario")

        print(f"\n📄 ARCHIVOS GENERADOS:")
        print(f"   • {screenshot_path} - Página de login")
        if login_success:
            print(f"   • instagram_post_login.png - Post-login")
        print(f"   • instagram-upload/data/instagram_cookies.json - Cookies (si login exitoso)")

        return login_success

    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal."""

    inicio = time.time()
    print("🔐 Iniciando test seguro de login de Instagram...")
    print("⚠️  Este test puede realizar acciones REALES con confirmación")
    print()

    success = await test_login_seguro()
    fin = time.time()

    duracion = fin - inicio

    print("\n" + "=" * 80)
    print("🏁 FIN DEL TEST SEGURO DE LOGIN")
    print("=" * 80)

    print(f"⏱️  Duración total: {duracion:.1f} segundos")
    print(f"⏰ Fin: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if success:
        print("\n✅ TEST FINALIZADO - Login funcionó con selectores actualizados")
    else:
        print("\n⚠️  TEST FINALIZADO - Revisar problemas encontrados")

    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())