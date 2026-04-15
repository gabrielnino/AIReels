#!/usr/bin/env python3
"""
🧪 EXP-002: Verificar formulario de login visible
Ciclo: IMPLEMENTACIÓN → PRUEBA → RESULTADO → REPLANTEO
Basado en éxito de EXP-001
"""

import asyncio
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class Experiment002:
    """Experimento 002: Verificar formulario de login."""

    def __init__(self):
        self.experiment_id = "exp_002"
        self.config = self.load_config()
        self.start_time = time.time()
        self.results = {
            "success": False,
            "errors": [],
            "warnings": [],
            "screenshots": [],
            "metrics": {},
            "element_selectors": {
                "username": ['input[name="username"]', 'input[name="email"]', 'input[type="text"]'],
                "password": ['input[name="password"]', 'input[type="password"]'],
                "login_button": ['button[type="submit"]', 'div[role="button"]:has-text("Log in")']
            }
        }
        self.experiment_dir = Path(f"experiments/{self.experiment_id}")

    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración."""
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def run_step(self, step_name: str, step_func) -> bool:
        """Ejecutar paso con logging."""
        print(f"\n🔧 [{self.experiment_id}] PASO: {step_name}")
        try:
            result = await step_func()
            print(f"   ✅ {result}")
            return True
        except Exception as e:
            error_msg = f"{step_name}: {str(e)}"
            print(f"   ❌ Error: {error_msg}")
            self.results["errors"].append(error_msg)
            return False

    async def setup_browser(self):
        """IMPLEMENTACIÓN: Configurar navegador humano."""
        from playwright.async_api import async_playwright

        self.playwright = await async_playwright().start()

        browser = await self.playwright.chromium.launch(
            headless=self.config['browser_config']['headless'],
            slow_mo=self.config['browser_config']['slow_mo'],
            args=['--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(
            viewport=self.config['browser_config']['viewport'],
            user_agent=self.config['browser_config']['user_agent'],
            extra_http_headers=self.config['browser_config']['extra_http_headers']
        )

        self.page = await context.new_page()
        self.page.set_default_timeout(30000)

        return browser

    async def navigate_to_instagram(self):
        """Navegar a Instagram (reutilizando éxito de EXP-001)."""
        start_nav = time.time()

        try:
            await self.page.goto(
                'https://www.instagram.com/',
                wait_until='networkidle',
                timeout=30000
            )

            load_time = time.time() - start_nav
            self.results["metrics"]["load_time_seconds"] = round(load_time, 2)

            # Capturar screenshot inicial
            await self.capture_screenshot("initial_page")

            return f"Cargado en {load_time:.1f}s, URL: {self.page.url}"

        except Exception as e:
            await self.capture_screenshot("navigation_error")
            raise e

    async def check_login_form_present(self):
        """Verificar si formulario de login está presente."""
        start_check = time.time()

        # Selectores comunes para formulario de login
        form_selectors = [
            'form[action="/accounts/login/"]',
            'div[role="dialog"] form',
            'form input[name="username"]',
            'form input[name="password"]'
        ]

        form_found = False
        form_details = {}

        for selector in form_selectors:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    form_found = True
                    form_details[selector] = count
                    print(f"   📋 Selector encontrado: {selector} ({count} elementos)")
            except:
                continue

        check_time = time.time() - start_check
        self.results["metrics"]["form_detection_time"] = round(check_time, 2)
        self.results["metrics"]["form_selectors_found"] = form_details

        if form_found:
            await self.capture_screenshot("login_form_found")
            return f"Formulario detectado ({len(form_details)} selectores)"
        else:
            self.results["warnings"].append("Formulario de login no encontrado con selectores estándar")
            return "Formulario no encontrado con selectores estándar"

    async def verify_username_field(self):
        """Verificar campo de usuario."""
        username_found = False
        username_selectors = self.results["element_selectors"]["username"]

        for selector in username_selectors:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    username_found = True
                    # Verificar que sea interactivo
                    is_enabled = await self.page.locator(selector).first.is_enabled()
                    is_visible = await self.page.locator(selector).first.is_visible()

                    self.results["metrics"]["username_selector"] = selector
                    self.results["metrics"]["username_enabled"] = is_enabled
                    self.results["metrics"]["username_visible"] = is_visible

                    if is_enabled and is_visible:
                        await self.capture_screenshot("username_field")
                        return f"Campo usuario encontrado: {selector} (interactivo)"
                    else:
                        return f"Campo usuario encontrado: {selector} (pero no interactivo)"
            except:
                continue

        if not username_found:
            self.results["errors"].append("Campo de usuario no encontrado")
            return "❌ Campo de usuario no encontrado"

    async def verify_password_field(self):
        """Verificar campo de contraseña."""
        password_found = False
        password_selectors = self.results["element_selectors"]["password"]

        for selector in password_selectors:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    password_found = True
                    # Verificar que sea interactivo
                    is_enabled = await self.page.locator(selector).first.is_enabled()
                    is_visible = await self.page.locator(selector).first.is_visible()

                    self.results["metrics"]["password_selector"] = selector
                    self.results["metrics"]["password_enabled"] = is_enabled
                    self.results["metrics"]["password_visible"] = is_visible

                    if is_enabled and is_visible:
                        await self.capture_screenshot("password_field")
                        return f"Campo contraseña encontrado: {selector} (interactivo)"
                    else:
                        return f"Campo contraseña encontrado: {selector} (pero no interactivo)"
            except:
                continue

        if not password_found:
            self.results["errors"].append("Campo de contraseña no encontrado")
            return "❌ Campo de contraseña no encontrado"

    async def verify_login_button(self):
        """Verificar botón de login."""
        button_found = False
        button_selectors = self.results["element_selectors"]["login_button"]

        for selector in button_selectors:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    button_found = True
                    # Verificar que sea clickeable
                    is_enabled = await self.page.locator(selector).first.is_enabled()
                    is_visible = await self.page.locator(selector).first.is_visible()

                    self.results["metrics"]["login_button_selector"] = selector
                    self.results["metrics"]["login_button_enabled"] = is_enabled
                    self.results["metrics"]["login_button_visible"] = is_visible

                    if is_enabled and is_visible:
                        # Intentar hacer hover (comportamiento humano)
                        await self.page.locator(selector).first.hover()
                        await asyncio.sleep(0.5)
                        await self.capture_screenshot("login_button")
                        return f"Botón login encontrado: {selector} (clickeable)"
                    else:
                        return f"Botón login encontrado: {selector} (pero no clickeable)"
            except:
                continue

        if not button_found:
            self.results["warnings"].append("Botón de login no encontrado con selectores estándar")
            return "⚠️ Botón de login no encontrado"

    async def capture_screenshot(self, name: str):
        """Capturar screenshot."""
        screenshot_dir = self.experiment_dir / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)

        screenshot_path = screenshot_dir / f"{name}_{int(time.time())}.png"
        await self.page.screenshot(path=str(screenshot_path), full_page=True)
        self.results["screenshots"].append(str(screenshot_path))

        return screenshot_path

    def save_results(self):
        """RESULTADO: Guardar resultados."""
        # Guardar configuración usada
        config_file = self.experiment_dir / "config_used.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

        # Guardar resultados
        results_file = self.experiment_dir / "results.md"
        results_file.write_text(self.generate_report())

        print(f"\n📊 Resultados guardados en: {self.experiment_dir}")

    def generate_report(self) -> str:
        """Generar reporte del experimento."""
        duration = time.time() - self.start_time

        # Determinar éxito basado en criterios
        has_critical_errors = any("no encontrado" in err.lower() for err in self.results["errors"])
        form_detected = self.results["metrics"].get("form_selectors_found", {})

        if not has_critical_errors and len(form_detected) > 0:
            status_icon = "✅"
            status_text = "EXITOSO"
            self.results["success"] = True
        else:
            status_icon = "⚠️" if len(self.results["warnings"]) > 0 else "❌"
            status_text = "CON ADVERTENCIAS" if len(self.results["warnings"]) > 0 else "FALLIDO"
            self.results["success"] = False

        report = f"""# 🧪 EXP-002: Verificar formulario de login visible

## 📊 RESULTADOS
{status_icon} **Estado:** {status_text}
⏱️ **Duración total:** {duration:.1f} segundos
📸 **Screenshots:** {len(self.results['screenshots'])}
🚨 **Errores:** {len(self.results['errors'])}
⚠️ **Advertencias:** {len(self.results['warnings'])}

## 🎯 OBJETIVO
{self.config.get('objective', 'No especificado')}

## 🤔 HIPÓTESIS
{self.config.get('hypothesis', 'No especificada')}

## 📈 MÉTRICAS RECOLECTADAS
"""
        # Métricas
        for name, value in self.results["metrics"].items():
            if isinstance(value, dict):
                report += f"- **{name}:**\n"
                for k, v in value.items():
                    report += f"  - {k}: {v}\n"
            else:
                report += f"- **{name}:** {value}\n"

        # Errores
        if self.results["errors"]:
            report += "\n## 🚨 ERRORES ENCONTRADOS\n"
            for error in self.results["errors"]:
                report += f"- {error}\n"

        # Advertencias
        if self.results["warnings"]:
            report += "\n## ⚠️ ADVERTENCIAS\n"
            for warning in self.results["warnings"]:
                report += f"- {warning}\n"

        # Screenshots
        if self.results["screenshots"]:
            report += "\n## 📸 EVIDENCIA VISUAL\n"
            for screenshot in self.results["screenshots"]:
                filename = Path(screenshot).name
                report += f"![{filename}](screenshots/{filename})\n"

        # Conclusión
        report += f"""
## 🎯 CONCLUSIÓN
"""
        if self.results["success"]:
            report += """✅ HIPÓTESIS VALIDADA: Formulario de login está presente y accesible
- Campos de usuario y contraseña detectados
- Botón de login encontrado
- Listo para proceder con ingreso de credenciales"""
        else:
            report += """⚠️ HIPÓTESIS PARCIALMENTE VALIDADA/REFUTADA
- Posiblemente ya estamos logueados
- O formulario usa selectores diferentes
- Requiere investigación adicional"""

        # Recomendación para siguiente experimento
        report += f"""
## 📝 RECOMENDACIÓN PARA SIGUIENTE EXPERIMENTO
"""
        if self.results["success"]:
            report += """**EXP-003:** Ingreso de credenciales de prueba
- Objetivo: Ingresar usuario y contraseña en campos detectados
- Hipótesis: Campos son editables y aceptan entrada"""
        else:
            report += """**EXP-002b:** Verificar estado de login actual
- Objetivo: Determinar si ya estamos autenticados
- Hipótesis: Usuario ya está logueado (cookie de sesión activa)"""

        report += f"""
---
*Ejecutado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Duración: {duration:.1f} segundos*
*Basado en éxito de EXP-001*
"""
        return report

async def main():
    """Ejecutar ciclo completo del experimento."""
    print("=" * 70)
    print("🧪 EXP-002: INICIANDO CICLO DE EXPERIMENTACIÓN")
    print("=" * 70)
    print("📋 Basado en éxito de EXP-001 (navegación funcional)")

    exp = Experiment002()
    browser = None

    try:
        print("\n1️⃣ IMPLEMENTACIÓN: Configurando entorno...")

        # Paso 1: Setup navegador
        setup_success = await exp.run_step("Setup navegador humano",
                                          exp.setup_browser)
        if not setup_success:
            exp.results["success"] = False
            raise Exception("Setup de navegador falló")

        browser = await exp.setup_browser()

        print("\n2️⃣ PRUEBA REAL: Verificando formulario de login...")

        # Paso 2: Navegar (ya probado en EXP-001)
        nav_success = await exp.run_step("Navegar a instagram.com",
                                        exp.navigate_to_instagram)
        if not nav_success:
            exp.results["success"] = False
            await exp.capture_screenshot("navigation_failed")
            raise Exception("Navegación falló")

        # Paso 3: Verificar formulario
        form_success = await exp.run_step("Buscar formulario de login",
                                         exp.check_login_form_present)

        # Paso 4: Verificar campos específicos
        if form_success:
            await exp.run_step("Verificar campo de usuario",
                             exp.verify_username_field)
            await exp.run_step("Verificar campo de contraseña",
                             exp.verify_password_field)
            await exp.run_step("Verificar botón de login",
                             exp.verify_login_button)

        print("\n3️⃣ RESULTADO: Analizando datos...")

        # Determinar éxito basado en criterios
        has_critical_errors = any("no encontrado" in err.lower()
                                 for err in exp.results["errors"])
        form_detected = exp.results["metrics"].get("form_selectors_found", {})

        exp.results["success"] = not has_critical_errors and len(form_detected) > 0

        # Guardar resultados
        exp.save_results()

        print("\n4️⃣ REPLANTEO: Tomando decisión basada en resultados...")

        if exp.results["success"]:
            print(f"""
🎉 EXP-002 EXITOSO: Formulario de login detectado

👉 DECISIÓN: Proceder con EXP-003 - Ingreso de credenciales
   - Campos encontrados: {exp.results['metrics'].get('username_selector', 'N/A')}, {exp.results['metrics'].get('password_selector', 'N/A')}
   - Siguiente: Probar ingreso de usuario/contraseña""")
        else:
            print(f"""
🔧 EXP-002 CON PROBLEMAS: {len(exp.results['errors'])} errores, {len(exp.results['warnings'])} advertencias

👉 DECISIÓN: {'Crear EXP-002b - Verificar estado de login' if 'ya estamos logueados' in str(exp.results['warnings']) else 'Revisar selectores de formulario'}
   - Problemas: {exp.results['errors'][0] if exp.results['errors'] else exp.results['warnings'][0] if exp.results['warnings'] else 'Desconocido'}
   - Siguiente: Investigar estado actual de sesión""")

    except Exception as e:
        print(f"\n🚨 ERROR NO MANEJADO: {str(e)}")
        exp.results["errors"].append(f"Error no manejado: {str(e)}")
        exp.results["success"] = False
        exp.save_results()

    finally:
        # Limpiar
        if browser:
            await browser.close()
            if hasattr(exp, 'playwright'):
                await exp.playwright.stop()

        print(f"\n{'='*70}")
        print(f"🏁 CICLO EXP-002 COMPLETADO")
        print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())