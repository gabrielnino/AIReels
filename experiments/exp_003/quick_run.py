#!/usr/bin/env python3
"""
🧪 EXP-003: Login completo RÁPIDO
Ciclo: IMPLEMENTACIÓN → PRUEBA → RESULTADO → REPLANTEO
Basado en hallazgos de EXP-001, EXP-002, EXP-002b
"""

import asyncio
import time
import os
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("🚀 EXP-003: LOGIN COMPLETO CON CREDENCIALES")
print("=" * 70)
print("📋 Basado en hallazgos previos:")
print("   - EXP-001: ✅ Navegación funciona")
print("   - EXP-002: ⚠️  Campos visibles (email, password)")
print("   - EXP-002b: ❌ NO autenticados (22% confianza)")

async def quick_login_experiment():
    """Experimento rápido de login."""
    from playwright.async_api import async_playwright

    results = {
        "experiment_id": "exp_003",
        "start_time": time.time(),
        "success": False,
        "steps_completed": [],
        "errors": [],
        "screenshots": []
    }

    # Crear directorio
    exp_dir = Path("experiments/exp_003")
    exp_dir.mkdir(exist_ok=True)

    playwright = None
    browser = None
    page = None

    try:
        print("\n1️⃣ IMPLEMENTACIÓN: Configurando con lo aprendido...")

        # Cargar credenciales
        env_path = Path(__file__).parent.parent.parent / "instagram-upload" / ".env.instagram"
        if not env_path.exists():
            print("❌ No existe .env.instagram")
            return False

        credentials = {}
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    credentials[key] = value

        username = credentials.get('INSTAGRAM_USERNAME', '')
        password = credentials.get('INSTAGRAM_PASSWORD', '')

        if not username or not password:
            print("❌ Credenciales no configuradas")
            return False

        print(f"   👤 Usuario: {username}")
        print(f"   🔑 Contraseña: {'*' * len(password)}")

        # Configuración probada en EXP-001
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=1000,  # Comportamiento humano
            args=['--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = await context.new_page()
        page.set_default_timeout(30000)

        results["steps_completed"].append("setup_complete")

        print("\n2️⃣ PRUEBA REAL: Ejecutando login...")

        # Paso 1: Navegar (ya probado en EXP-001)
        print("   🌐 Navegando a Instagram...")
        await page.goto('https://www.instagram.com/', wait_until='networkidle')
        await asyncio.sleep(2)

        # Capturar estado inicial
        await page.screenshot(path=str(exp_dir / "01_initial.png"))
        results["screenshots"].append("01_initial.png")
        results["steps_completed"].append("navigation_complete")

        # Paso 2: Verificar campos (basado en EXP-002)
        print("   🔍 Buscando campos de login...")

        # Selectores encontrados en EXP-002
        username_selector = 'input[name="email"]'  # Encontrado en EXP-002
        password_selector = 'input[type="password"]'  # Encontrado en EXP-002
        login_button_selector = 'div[role="button"]:has-text("Log in")'  # Encontrado en EXP-002

        # Verificar que campos existen
        username_exists = await page.locator(username_selector).count() > 0
        password_exists = await page.locator(password_selector).count() > 0
        button_exists = await page.locator(login_button_selector).count() > 0

        print(f"   📋 Campos encontrados: Usuario={username_exists}, Password={password_exists}, Botón={button_exists}")

        if not (username_exists and password_exists and button_exists):
            print("   ❌ Campos no encontrados - tomando screenshot")
            await page.screenshot(path=str(exp_dir / "02_fields_missing.png"), full_page=True)
            results["errors"].append("Campos de login no encontrados")
            return False

        results["steps_completed"].append("fields_found")
        await page.screenshot(path=str(exp_dir / "02_fields_found.png"))
        results["screenshots"].append("02_fields_found.png")

        # Paso 3: Ingresar credenciales
        print("   ⌨️  Ingresando credenciales...")

        # Comportamiento humano: click, esperar, escribir
        await page.locator(username_selector).first.click()
        await asyncio.sleep(0.5)
        await page.locator(username_selector).first.fill(username)
        await asyncio.sleep(0.5)

        await page.locator(password_selector).first.click()
        await asyncio.sleep(0.5)
        await page.locator(password_selector).first.fill(password)
        await asyncio.sleep(1)

        await page.screenshot(path=str(exp_dir / "03_credentials_entered.png"))
        results["screenshots"].append("03_credentials_entered.png")
        results["steps_completed"].append("credentials_entered")

        # Paso 4: Click en login
        print("   🖱️  Click en botón Login...")

        # Verificar que botón está habilitado (no como en EXP-002)
        is_enabled = await page.locator(login_button_selector).first.is_enabled()
        print(f"   🔘 Botón habilitado: {is_enabled}")

        if is_enabled:
            await page.locator(login_button_selector).first.click()
            await asyncio.sleep(5)  # Esperar respuesta de login

            # Capturar después del click
            await page.screenshot(path=str(exp_dir / "04_after_login_click.png"))
            results["screenshots"].append("04_after_login_click.png")
            results["steps_completed"].append("login_clicked")

            # Paso 5: Verificar resultado
            print("   🔍 Verificando resultado de login...")

            current_url = page.url
            page_title = await page.title()

            print(f"   🌐 URL actual: {current_url}")
            print(f"   📄 Título: {page_title}")

            # Indicadores de login exitoso (basado en EXP-002b)
            indicators = {
                "home_icon": await page.locator('svg[aria-label="Home"]').count() > 0,
                "search_icon": await page.locator('svg[aria-label="Search"]').count() > 0,
                "create_icon": await page.locator('svg[aria-label="New post"]').count() > 0,
                "profile_icon": await page.locator('svg[aria-label="Profile"]').count() > 0,
                "not_logged_in": 'login' in current_url or 'accounts' in current_url,
                "two_factor": 'two-factor' in current_url or '2fa' in current_url.lower()
            }

            print(f"   📊 Indicadores: Home={indicators['home_icon']}, Search={indicators['search_icon']}, Login_page={indicators['not_logged_in']}")

            # Determinar resultado
            if indicators['two_factor']:
                print("   🔢 2FA DETECTADO - Esperando código manual")
                results["steps_completed"].append("two_factor_detected")
                await page.screenshot(path=str(exp_dir / "05_2fa_detected.png"))
                results["screenshots"].append("05_2fa_detected.png")

                # Pausa para entrada manual de 2FA
                print("   ⏳ Pausando 30 segundos para entrada manual de 2FA...")
                print("   📱 Revisa Instagram en tu teléfono y ingresa el código")

                for i in range(30, 0, -1):
                    print(f"   ⏰ {i}...", end='\r')
                    await asyncio.sleep(1)
                print()

                # Verificar si login completado después de 2FA
                await page.screenshot(path=str(exp_dir / "06_after_2fa_wait.png"))
                results["screenshots"].append("06_after_2fa_wait.png")

                # Re-evaluar indicadores
                indicators_after = {
                    "home_icon": await page.locator('svg[aria-label="Home"]').count() > 0,
                    "logged_in": not ('login' in page.url or 'accounts' in page.url)
                }

                if indicators_after['home_icon'] and indicators_after['logged_in']:
                    print("   ✅ LOGIN EXITOSO (con 2FA manual)")
                    results["success"] = True
                else:
                    print("   ❌ Login aún no completado después de 2FA")
                    results["errors"].append("2FA no completado manualmente")

            elif indicators['home_icon'] and indicators['search_icon'] and not indicators['not_logged_in']:
                print("   ✅ LOGIN EXITOSO (sin 2FA)")
                results["success"] = True
                await page.screenshot(path=str(exp_dir / "05_login_success.png"))
                results["screenshots"].append("05_login_success.png")

            elif indicators['not_logged_in']:
                print("   ❌ LOGIN FALLIDO - Aún en página de login")
                results["errors"].append("Login falló - aún en página de login")
                await page.screenshot(path=str(exp_dir / "05_login_failed.png"), full_page=True)
                results["screenshots"].append("05_login_failed.png")

            else:
                print("   ⚠️  ESTADO INDETERMINADO")
                results["errors"].append("Estado de login indeterminado")
                await page.screenshot(path=str(exp_dir / "05_indeterminate.png"), full_page=True)
                results["screenshots"].append("05_indeterminate.png")

        else:
            print("   ❌ Botón de login NO habilitado (mismo problema que EXP-002)")
            results["errors"].append("Botón de login no habilitado")
            await page.screenshot(path=str(exp_dir / "04_button_disabled.png"), full_page=True)
            results["screenshots"].append("04_button_disabled.png")

        print("\n3️⃣ RESULTADO: Analizando...")

        duration = time.time() - results["start_time"]
        results["duration"] = duration

        # Generar reporte rápido
        report = f"""# 🧪 EXP-003: Login completo con credenciales

## 📊 RESULTADOS
{'✅' if results['success'] else '❌'} **Estado:** {'EXITOSO' if results['success'] else 'FALLIDO'}
⏱️ **Duración:** {duration:.1f} segundos
📸 **Screenshots:** {len(results['screenshots'])}
🚨 **Errores:** {len(results['errors'])}
📋 **Pasos completados:** {len(results['steps_completed'])}

## 🎯 OBJETIVO
Login automático completo basado en hallazgos de experimentos previos.

## 📈 DATOS
- **Usuario:** {username}
- **URL inicial:** https://www.instagram.com/
- **Pasos:** {', '.join(results['steps_completed'][:3])}...

"""

        if results["errors"]:
            report += "## 🚨 ERRORES\n"
            for error in results["errors"]:
                report += f"- {error}\n"

        if results["screenshots"]:
            report += "\n## 📸 EVIDENCIA\n"
            for screenshot in results["screenshots"]:
                report += f"![{screenshot}]({screenshot})\n"

        # Conclusión y siguiente paso
        report += f"""
## 🎯 CONCLUSIÓN
{'✅ LOGIN EXITOSO' if results['success'] else '❌ LOGIN FALLIDO'}

## 📝 SIGUIENTE EXPERIMENTO
"""
        if results["success"]:
            report += "**EXP-004:** Navegación a página de upload\n- Objetivo: Acceder a /create después de login exitoso\n- Hipótesis: Podemos navegar directamente a upload"
        else:
            if "2FA" in str(results["errors"]):
                report += "**EXP-003b:** Manejo automático de 2FA\n- Objetivo: Implementar entrada automática de código 2FA\n- Hipótesis: Podemos detectar y manejar 2FA programáticamente"
            elif "Botón de login no habilitado" in str(results["errors"]):
                report += "**EXP-003c:** Habilitar botón de login\n- Objetivo: Descubrir por qué botón está deshabilitado\n- Hipótesis: Validación de campos requerida"
            else:
                report += "**EXP-003b:** Debug detallado de login\n- Objetivo: Identificar causa exacta de fallo\n- Hipótesis: Selectores o flujo incorrectos"

        report += f"""
---
*Ejecutado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Basado en: EXP-001 (navegación), EXP-002 (campos), EXP-002b (no autenticado)*
"""

        # Guardar reporte
        report_path = exp_dir / "quick_results.md"
        report_path.write_text(report)

        print(f"\n📄 Reporte guardado en: {report_path}")

        print("\n4️⃣ REPLANTEO: Decisión final...")

        if results["success"]:
            print(f"""
🎉 **LOGIN EXITOSO!**

👉 DECISIÓN: Proceder con upload flow
   - Tiempo: {duration:.1f}s
   - Pasos: {len(results['steps_completed'])}
   - Siguiente: EXP-004 - Navegación a /create""")
        else:
            print(f"""
🔧 **LOGIN FALLIDO**

👉 DECISIÓN: {'Manejo de 2FA' if '2FA' in str(results['errors']) else 'Debug de botón login' if 'botón' in str(results['errors']).lower() else 'Investigación adicional'}
   - Errores: {results['errors'][0] if results['errors'] else 'Desconocido'}
   - Siguiente: EXP-003b - {'Manejo de 2FA' if '2FA' in str(results['errors']) else 'Debug detallado'}""")

        return results["success"]

    except Exception as e:
        print(f"\n🚨 ERROR NO MANEJADO: {str(e)}")
        import traceback
        traceback.print_exc()

        if exp_dir and page:
            try:
                await page.screenshot(path=str(exp_dir / "error.png"), full_page=True)
            except:
                pass

        return False

    finally:
        # Limpiar
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

async def main():
    """Ejecutar experimento."""
    success = await quick_login_experiment()

    print(f"\n{'='*70}")
    print(f"🏁 EXP-003 {'COMPLETADO EXITOSAMENTE' if success else 'FALLÓ - REQUIERE AJUSTES'}")
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())