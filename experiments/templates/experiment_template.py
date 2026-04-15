#!/usr/bin/env python3
"""
🧪 PLANTILLA DE EXPERIMENTO - Ciclo: Implementación → Prueba → Resultado → Replanteo
"""

import asyncio
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class BaseExperiment:
    """Clase base para todos los experimentos."""

    def __init__(self, experiment_id: str, config_path: str):
        self.experiment_id = experiment_id
        self.config = self.load_config(config_path)
        self.start_time = time.time()
        self.results = {
            "success": False,
            "errors": [],
            "warnings": [],
            "screenshots": [],
            "metrics": {},
            "raw_data": {}
        }

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Cargar configuración desde YAML."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def run_step(self, step_name: str, step_func) -> bool:
        """Ejecutar un paso del experimento con logging."""
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

    def record_metric(self, name: str, value: Any):
        """Registrar una métrica."""
        self.results["metrics"][name] = value

    async def capture_screenshot(self, page, filename: str):
        """Capturar screenshot y guardar."""
        screenshot_path = self.experiment_dir / "screenshots" / f"{filename}.png"
        screenshot_path.parent.mkdir(exist_ok=True)

        await page.screenshot(path=str(screenshot_path))
        self.results["screenshots"].append(str(screenshot_path))
        return screenshot_path

    def save_results(self):
        """Guardar resultados del experimento."""
        # Crear directorio del experimento
        self.experiment_dir = Path(f"experiments/{self.experiment_id}")
        self.experiment_dir.mkdir(exist_ok=True)

        # Guardar configuración usada
        config_file = self.experiment_dir / "config_used.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

        # Guardar resultados
        results_file = self.experiment_dir / "results.md"
        results_file.write_text(self.generate_report())

        # Guardar datos crudos
        raw_file = self.experiment_dir / "raw_data.json"
        import json
        raw_file.write_text(json.dumps(self.results, indent=2, default=str))

        print(f"\n📊 Resultados guardados en: {self.experiment_dir}")

    def generate_report(self) -> str:
        """Generar reporte Markdown del experimento."""
        duration = time.time() - self.start_time

        status_icon = "✅" if self.results["success"] else "❌"
        status_text = "EXITOSO" if self.results["success"] else "FALLIDO"

        report = f"""# 🧪 {self.experiment_id}: {self.config.get('title', 'Sin título')}

## 📊 RESULTADOS
{status_icon} **Estado:** {status_text}
⏱️ **Duración:** {duration:.1f} segundos
📸 **Screenshots:** {len(self.results['screenshots'])}
🚨 **Errores:** {len(self.results['errors'])}
⚠️ **Advertencias:** {len(self.results['warnings'])}

## 🎯 OBJETIVO
{self.config.get('objective', 'No especificado')}

## 🤔 HIPÓTESIS
{self.config.get('hypothesis', 'No especificada')}

"""
        # Métricas
        if self.results["metrics"]:
            report += "## 📈 MÉTRICAS\n"
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

        # Conclusión y siguiente paso
        report += f"""
## 🎯 CONCLUSIÓN
{"✅ Hipótesis validada" if self.results["success"] else "❌ Hipótesis refutada"}

## 📝 RECOMENDACIÓN PARA SIGUIENTE EXPERIMENTO
[Basado en resultados, ¿qué probar después?]

---
*Ejecutado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Duración: {duration:.1f} segundos*
"""
        return report

# Ejemplo de implementación concreta
class InstagramExperiment(BaseExperiment):
    """Experimento específico para Instagram."""

    async def setup_human_browser(self):
        """Configurar navegador con comportamiento humano."""
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
        return browser

    async def cleanup(self, browser):
        """Limpiar recursos."""
        await browser.close()
        await self.playwright.stop()

async def main():
    """Ejecutar experimento."""
    # Configurar experimento
    exp = InstagramExperiment("exp_001", "experiments/exp_001/config.yaml")

    try:
        # IMPLEMENTACIÓN: Setup
        browser = await exp.setup_human_browser()

        # PRUEBA REAL: Ejecutar pasos
        for step in exp.config['test_scenario']['steps']:
            # Aquí implementar cada paso específico
            success = await exp.run_step(step, lambda: execute_step(step, exp.page))
            if not success:
                break

        # RESULTADO: Determinar éxito
        exp.results["success"] = len(exp.results["errors"]) == 0

    except Exception as e:
        exp.results["errors"].append(f"Error general: {str(e)}")
        exp.results["success"] = False
    finally:
        # Limpiar
        if 'browser' in locals():
            await exp.cleanup(browser)

        # Guardar resultados
        exp.save_results()

        # REPLANTEO: Mostrar decisión
        print(f"\n{'🎉' if exp.results['success'] else '🔧'} {exp.experiment_id} COMPLETADO")
        print(f"👉 {'Continuar con siguiente experimento' if exp.results['success'] else 'Ajustar y repetir'}")

if __name__ == "__main__":
    asyncio.run(main())