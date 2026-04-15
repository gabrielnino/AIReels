#!/usr/bin/env python3
"""
🧪 EXP-001: Navegación básica a Instagram sin NET::ERR_ABORTED
Ciclo: IMPLEMENTACIÓN → PRUEBA → RESULTADO → REPLANTEO
"""

import asyncio
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class Experiment001:
    """Experimento 001: Navegación básica."""

    def __init__(self):
        self.experiment_id = "exp_001"
        self.config = self.load_config()
        self.start_time = time.time()
        self.results = {
            "success": False,
            "errors": [],
            "warnings": [],
            "screenshots": [],
            "metrics": {},
            "raw_data": {}
        }
        self.experiment_dir = Path(f"experiments/{self.experiment_id}")

    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración."""
        config_path = Path(__file__).parent / "config_fixed.yaml"
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

        # Configuración humana
        browser = await self.playwright.chromium.launch(
            headless=self.config['browser_config']['headless'],
            slow_mo=self.config['browser_config']['slow_mo'],
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        context = await browser.new_context(
            viewport=self.config['browser_config']['viewport'],
            user_agent=self.config['browser_config']['user_agent'],
            extra_http_headers=self.config['browser_config']['extra_http_headers'],
            java_script_enabled=True
        )

        self.page = await context.new_page()

        # Configurar timeouts
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)

        return browser

    async def navigate_to_instagram(self):
        """PRUEBA REAL: Navegar a Instagram."""
        start_nav = time.time()

        try:
            await self.page.goto(
                'https://www.instagram.com/',
                wait_until='networkidle',
                timeout=30000
            )

            load_time = time.time() - start_nav
            self.results["metrics"]["load_time_seconds"] = round(load_time, 2)

            return f"Cargado en {load_time:.1f}s, URL: {self.page.url}"

        except Exception as e:
            # Capturar screenshot del error
            await self.capture_screenshot("navigation_error")
            raise e

    async def verify_page_loaded(self):
        """Verificar que página cargó correctamente."""
        checks = []

        # Check 1: Título contiene Instagram
        title = await self.page.title()
        checks.append(("Título contiene 'Instagram'", "Instagram" in title))
        self.results["metrics"]["page_title"] = title

        # Check 2: URL es Instagram
        current_url = self.page.url
        checks.append(("URL es instagram.com", "instagram.com" in current_url))
        self.results["metrics"]["final_url"] = current_url

        # Check 3: Elementos clave visibles
        try:
            instagram_logo = await self.page.locator('svg[aria-label="Instagram"]').count()
            checks.append(("Logo Instagram visible", instagram_logo > 0))
        except:
            checks.append(("Logo Instagram visible", False))

        # Evaluar checks
        all_passed = all(passed for _, passed in checks)

        if not all_passed:
            failed_checks = [name for name, passed in checks if not passed]
            self.results["warnings"].append(f"Checks fallidos: {', '.join(failed_checks)}")

        return f"Checks: {sum(passed for _, passed in checks)}/{len(checks)} OK"

    async def check_network_errors(self):
        """Verificar errores de red."""
        # Revisar errores de consola
        console_errors = await self.page.evaluate("""() => {
            return window.console && window.console.error
                ? Array.from(window.console.error).slice(-5)
                : [];
        }""")

        self.results["metrics"]["console_errors_count"] = len(console_errors)

        # Buscar NET::ERR_ABORTED específicamente
        net_errors = [err for err in console_errors if "NET::ERR_ABORTED" in str(err)]

        if net_errors:
            self.results["errors"].append(f"NET::ERR_ABORTED encontrado: {net_errors[0]}")
            return f"❌ NET::ERR_ABORTED detectado"
        else:
            return "✅ Sin errores NET::ERR_ABORTED"

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

        status_icon = "✅" if self.results["success"] else "❌"
        status_text = "EXITOSO" if self.results["success"] else "FALLIDO"

        report = f"""# 🧪 EXP-001: Navegación básica a Instagram sin NET::ERR_ABORTED

## 📊 RESULTADOS
{status_icon} **Estado:** {status_text}
⏱️ **Duración total:** {duration:.1f} segundos
📸 **Screenshots:** {len(self.results['screenshots'])}
🚨 **Errores:** {len(self.results['errors'])}
⚠️ **Advertencias:** {len(self.results['warnings'])}

## 🎯 OBJETIVO
Probar que podemos navegar a Instagram.com sin recibir error NET::ERR_ABORTED
que indica detección de automation.

## 🤔 HIPÓTESIS
Configuración de navegador con comportamiento humano (headless=false, slow_mo=1000ms)
evita que Instagram detecte automation y bloquee la carga.

## 📈 MÉTRICAS RECOLECTADAS
"""
        # Métricas
        for name, value in self.results["metrics"].items():
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
{"✅ HIPÓTESIS VALIDADA: Navegación exitosa sin NET::ERR_ABORTED"
 if self.results["success"] else
 "❌ HIPÓTESIS REFUTADA: Instagram detecta automation"}

## 📝 RECOMENDACIÓN PARA SIGUIENTE EXPERIMENTO
"""
        if self.results["success"]:
            report += """**EXP-002:** Verificar formulario de login visible
- Objetivo: Confirmar que campo de usuario/contraseña son accesibles
- Hipótesis: Después de navegación exitosa, formulario de login está presente"""
        else:
            report += """**EXP-001b:** Ajustar configuración de navegador
- Objetivo: Encontrar configuración que evite detección
- Hipótesis: Cambios en user agent, viewport o headers resolverán"""

        report += f"""
---
*Ejecutado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Duración: {duration:.1f} segundos*
"""
        return report

async def main():
    """Ejecutar ciclo completo del experimento."""
    print("=" * 70)
    print("🧪 EXP-001: INICIANDO CICLO DE EXPERIMENTACIÓN")
    print("=" * 70)

    exp = Experiment001()
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

        print("\n2️⃣ PRUEBA REAL: Ejecutando con Instagram real...")

        # Paso 2: Navegar
        nav_success = await exp.run_step("Navegar a instagram.com",
                                        exp.navigate_to_instagram)
        if not nav_success:
            exp.results["success"] = False
            await exp.capture_screenshot("navigation_failed")

        # Paso 3: Verificar carga
        if nav_success:
            verify_success = await exp.run_step("Verificar página cargada",
                                               exp.verify_page_loaded)
            if verify_success:
                await exp.capture_screenshot("page_loaded")

        # Paso 4: Check errores de red
        if nav_success and verify_success:
            await exp.run_step("Verificar errores NET::ERR_ABORTED",
                              exp.check_network_errors)

        print("\n3️⃣ RESULTADO: Analizando datos...")

        # Determinar éxito basado en criterios
        has_net_error = any("NET::ERR_ABORTED" in err for err in exp.results["errors"])
        exp.results["success"] = not has_net_error and nav_success and verify_success

        # Guardar resultados
        exp.save_results()

        print("\n4️⃣ REPLANTEO: Tomando decisión basada en resultados...")

        if exp.results["success"]:
            print(f"""
🎉 EXP-001 EXITOSO: Navegación funcional sin errores de red

👉 DECISIÓN: Proceder con EXP-002 - Verificar formulario de login
   - Hipótesis validada: Configuración humana funciona
   - Siguiente: Confirmar que login es posible""")
        else:
            print(f"""
🔧 EXP-001 FALLIDO: Problemas detectados

👉 DECISIÓN: Crear EXP-001b - Ajustar configuración
   - Problema: {exp.results["errors"][0] if exp.results["errors"] else "Desconocido"}
   - Siguiente: Probar configuración alternativa""")

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
        print(f"🏁 CICLO EXP-001 COMPLETADO")
        print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())