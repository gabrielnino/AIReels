#!/usr/bin/env python3
"""
🧪 EXP-002b: Verificar estado de autenticación actual
Ciclo: IMPLEMENTACIÓN → PRUEBA → RESULTADO → REPLANTEO
Basado en resultados ambiguos de EXP-002
"""

import asyncio
import time
import yaml
from pathlib import Path
from datetime import datetime

class Experiment002b:
    """Experimento 002b: Verificar autenticación."""

    def __init__(self):
        self.experiment_id = "exp_002b"
        self.config = self.load_config()
        self.start_time = time.time()
        self.results = {
            "success": False,
            "errors": [],
            "warnings": [],
            "screenshots": [],
            "metrics": {},
            "authentication_state": "UNKNOWN",
            "indicators": {
                "authenticated": [],
                "not_authenticated": []
            }
        }
        self.experiment_dir = Path(f"experiments/{self.experiment_id}")

    def load_config(self):
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
        """Configurar navegador."""
        from playwright.async_api import async_playwright

        self.playwright = await async_playwright().start()
        browser = await self.playwright.chromium.launch(
            headless=self.config['browser_config']['headless'],
            slow_mo=self.config['browser_config']['slow_mo']
        )

        context = await browser.new_context(
            viewport=self.config['browser_config']['viewport'],
            user_agent=self.config['browser_config']['user_agent'],
            extra_http_headers=self.config['browser_config']['extra_http_headers']
        )

        self.page = await context.new_page()
        self.page.set_default_timeout(20000)

        return browser

    async def navigate_to_instagram(self):
        """Navegar a Instagram."""
        start = time.time()
        await self.page.goto('https://www.instagram.com/', wait_until='networkidle')

        load_time = time.time() - start
        self.results["metrics"]["load_time"] = round(load_time, 2)
        self.results["metrics"]["initial_url"] = self.page.url

        await self.capture_screenshot("initial_page")
        return f"Cargado en {load_time:.1f}s, URL: {self.page.url}"

    async def check_authentication_indicators(self):
        """Verificar indicadores de autenticación."""
        print("\n🔍 ANALIZANDO INDICADORES DE AUTENTICACIÓN:")

        # Indicadores de AUTENTICADO
        auth_indicators = [
            ("Profile icon visible", 'svg[aria-label="Profile"]'),
            ("Home icon visible", 'svg[aria-label="Home"]'),
            ("Create button visible", 'svg[aria-label="New post"]'),
            ("Search visible", 'svg[aria-label="Search"]'),
            ("Messages visible", 'svg[aria-label="Direct"]'),
        ]

        # Indicadores de NO AUTENTICADO
        no_auth_indicators = [
            ("Login form present", 'form[action*="login"]'),
            ("Sign up link", 'a[href*="/accounts/signup/"]'),
            ("Login button text", ':has-text("Log in"):visible'),
            ("Forgot password", 'a[href*="/accounts/password/reset/"]'),
        ]

        auth_score = 0
        total_checks = len(auth_indicators) + len(no_auth_indicators)

        # Check indicadores de autenticado
        for name, selector in auth_indicators:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    auth_score += 1
                    self.results["indicators"]["authenticated"].append(name)
                    print(f"   ✅ {name} - PRESENTE")
                else:
                    print(f"   ❌ {name} - AUSENTE")
            except:
                print(f"   ⚠️  {name} - ERROR")

        # Check indicadores de no autenticado
        for name, selector in no_auth_indicators:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    auth_score -= 1
                    self.results["indicators"]["not_authenticated"].append(name)
                    print(f"   ❌ {name} - PRESENTE (sugiere NO autenticado)")
                else:
                    print(f"   ✅ {name} - AUSENTE (sugiere autenticado)")
            except:
                print(f"   ⚠️  {name} - ERROR")

        # Calcular score de confianza
        confidence = (auth_score + len(no_auth_indicators)) / total_checks * 100
        self.results["metrics"]["auth_confidence"] = round(confidence, 1)
        self.results["metrics"]["auth_score"] = auth_score

        # Determinar estado
        if confidence > 70:
            self.results["authentication_state"] = "AUTHENTICATED"
            state = "✅ AUTENTICADO"
        elif confidence < 30:
            self.results["authentication_state"] = "NOT_AUTHENTICATED"
            state = "❌ NO AUTENTICADO"
        else:
            self.results["authentication_state"] = "UNCERTAIN"
            state = "⚠️  INDETERMINADO"

        await self.capture_screenshot("auth_indicators")
        return f"Estado: {state} (Confianza: {confidence:.0f}%)"

    async def verify_homepage_elements(self):
        """Verificar elementos específicos de homepage autenticada."""
        if self.results["authentication_state"] != "AUTHENTICATED":
            return "Saltado - No parece autenticado"

        homepage_elements = [
            ("Stories section", 'div[role="button"][tabindex="0"]:has(circle)'),
            ("Feed posts", 'article'),
            ("Suggested for you", ':has-text("Suggested for you")'),
            ("Navigation bar", 'nav'),
        ]

        found_elements = []
        for name, selector in homepage_elements:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    found_elements.append(name)
            except:
                continue

        self.results["metrics"]["homepage_elements_found"] = len(found_elements)

        if found_elements:
            await self.capture_screenshot("homepage_elements")
            return f"Elementos homepage: {', '.join(found_elements[:3])}"
        else:
            return "⚠️ Pocos elementos de homepage encontrados"

    async def test_navigation_to_profile(self):
        """Intentar navegar a perfil (solo si autenticado)."""
        if self.results["authentication_state"] != "AUTHENTICATED":
            return "Saltado - No autenticado"

        try:
            # Intentar click en icono de perfil
            profile_clicked = False
            profile_selectors = [
                'svg[aria-label="Profile"]',
                'a[href*="/accounts/edit/"]',
                'a[href*="/' + self.get_username() + '/"]'
            ]

            for selector in profile_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.locator(selector).first.click()
                        await asyncio.sleep(2)
                        profile_clicked = True

                        # Verificar que estamos en página de perfil
                        current_url = self.page.url
                        if "/accounts/edit/" in current_url or "/" + self.get_username() + "/" in current_url:
                            self.results["metrics"]["profile_access"] = "SUCCESS"
                            await self.capture_screenshot("profile_page")
                            return "✅ Navegación a perfil exitosa"
                        break
                except:
                    continue

            if not profile_clicked:
                self.results["metrics"]["profile_access"] = "FAILED"
                return "⚠️ No se pudo navegar a perfil"
            else:
                return "✅ Click en perfil ejecutado"

        except Exception as e:
            self.results["metrics"]["profile_access"] = "ERROR"
            return f"❌ Error navegando a perfil: {str(e)}"

    def get_username(self):
        """Obtener username de configuración."""
        # Intentar leer de .env.instagram
        env_path = Path(__file__).parent.parent.parent / "instagram-upload" / ".env.instagram"
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith("INSTAGRAM_USERNAME="):
                        return line.split("=")[1].strip()
        return "fiestacotoday"

    async def check_cookie_state(self):
        """Verificar estado de cookies."""
        try:
            cookies = await self.page.context.cookies()
            cookie_count = len(cookies)

            # Buscar cookies de sesión de Instagram
            session_cookies = [c for c in cookies if "sessionid" in c.get("name", "").lower()]
            ig_cookies = [c for c in cookies if "instagram" in c.get("domain", "").lower()]

            self.results["metrics"]["total_cookies"] = cookie_count
            self.results["metrics"]["session_cookies"] = len(session_cookies)
            self.results["metrics"]["instagram_cookies"] = len(ig_cookies)

            return f"Cookies: {cookie_count} total, {len(session_cookies)} de sesión"

        except Exception as e:
            return f"⚠️ Error leyendo cookies: {str(e)}"

    async def capture_screenshot(self, name: str):
        """Capturar screenshot."""
        screenshot_dir = self.experiment_dir / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)

        path = screenshot_dir / f"{name}_{int(time.time())}.png"
        await self.page.screenshot(path=str(path))
        self.results["screenshots"].append(str(path))
        return path

    def save_results(self):
        """Guardar resultados."""
        # Guardar configuración
        config_file = self.experiment_dir / "config_used.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

        # Guardar resultados
        results_file = self.experiment_dir / "results.md"
        results_file.write_text(self.generate_report())

        print(f"\n📊 Resultados guardados en: {self.experiment_dir}")

    def generate_report(self):
        """Generar reporte."""
        duration = time.time() - self.start_time

        # Determinar éxito
        has_clear_state = self.results["authentication_state"] in ["AUTHENTICATED", "NOT_AUTHENTICATED"]
        self.results["success"] = has_clear_state and len(self.results["errors"]) == 0

        status_icon = "✅" if self.results["success"] else "⚠️"
        status_text = "EXITOSO" if self.results["success"] else "CON ADVERTENCIAS"

        report = f"""# 🧪 EXP-002b: Verificar estado de autenticación actual

## 📊 RESULTADOS
{status_icon} **Estado:** {status_text}
⏱️ **Duración:** {duration:.1f} segundos
🔐 **Estado Autenticación:** {self.results['authentication_state']}
📸 **Screenshots:** {len(self.results['screenshots'])}
🚨 **Errores:** {len(self.results['errors'])}

## 🎯 OBJETIVO
Determinar el estado actual de autenticación después de navegar a Instagram.

## 🤔 HIPÓTESIS
Usuario 'fiestacotoday' ya tiene sesión activa en Instagram.

## 📈 MÉTRICAS RECOLECTADAS
"""
        # Métricas
        for name, value in self.results["metrics"].items():
            report += f"- **{name}:** {value}\n"

        # Indicadores
        report += f"\n## 🔍 INDICADORES ENCONTRADOS\n"

        if self.results["indicators"]["authenticated"]:
            report += "### ✅ SUGIERE AUTENTICADO:\n"
            for indicator in self.results["indicators"]["authenticated"]:
                report += f"- {indicator}\n"

        if self.results["indicators"]["not_authenticated"]:
            report += "\n### ❌ SUGIERE NO AUTENTICADO:\n"
            for indicator in self.results["indicators"]["not_authenticated"]:
                report += f"- {indicator}\n"

        # Errores
        if self.results["errors"]:
            report += "\n## 🚨 ERRORES\n"
            for error in self.results["errors"]:
                report += f"- {error}\n"

        # Screenshots
        if self.results["screenshots"]:
            report += "\n## 📸 EVIDENCIA VISUAL\n"
            for screenshot in self.results["screenshots"]:
                filename = Path(screenshot).name
                report += f"![{filename}](screenshots/{filename})\n"

        # Conclusión y recomendación
        report += f"""
## 🎯 CONCLUSIÓN
"""

        if self.results["authentication_state"] == "AUTHENTICATED":
            report += """✅ **YA ESTAMOS AUTENTICADOS EN INSTAGRAM**
- Explica resultados de EXP-002 (campos visibles pero formulario incompleto)
- No necesitamos hacer login
- Podemos proceder directamente a upload flow"""

            next_exp = "EXP-003: Navegación directa a página de upload"
            next_hypothesis = "Al estar autenticados, podemos navegar directamente a /create"

        elif self.results["authentication_state"] == "NOT_AUTHENTICATED":
            report += """❌ **NO ESTAMOS AUTENTICADOS**
- Necesitamos proceder con login completo
- Campos visibles en EXP-002 eran para login normal"""

            next_exp = "EXP-003: Login completo con credenciales"
            next_hypothesis = "Podemos hacer login automático con credenciales configuradas"

        else:
            report += """⚠️ **ESTADO INDETERMINADO**
- Evidencia conflictiva
- Necesita investigación adicional"""

            next_exp = "EXP-002c: Investigación profunda de estado"
            next_hypothesis = "Análisis más detallado revelará estado real"

        report += f"""
## 📝 RECOMENDACIÓN PARA SIGUIENTE EXPERIMENTO
**{next_exp}**
- Objetivo: {"Probar navegación a upload" if self.results['authentication_state'] == 'AUTHENTICATED' else "Realizar login completo"}
- Hipótesis: {next_hypothesis}

---
*Ejecutado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Basado en resultados de EXP-002*
"""
        return report

async def main():
    """Ejecutar experimento."""
    print("=" * 70)
    print("🧪 EXP-002b: VERIFICAR ESTADO DE AUTENTICACIÓN")
    print("=" * 70)
    print("📋 Basado en resultados ambiguos de EXP-002")

    exp = Experiment002b()
    browser = None

    try:
        print("\n1️⃣ IMPLEMENTACIÓN: Configurando...")

        browser = await exp.setup_browser()

        print("\n2️⃣ PRUEBA REAL: Analizando estado de autenticación...")

        await exp.run_step("Navegar a Instagram", exp.navigate_to_instagram)
        await exp.run_step("Analizar indicadores", exp.check_authentication_indicators)
        await exp.run_step("Verificar homepage", exp.verify_homepage_elements)
        await exp.run_step("Test navegación perfil", exp.test_navigation_to_profile)
        await exp.run_step("Verificar cookies", exp.check_cookie_state)

        print("\n3️⃣ RESULTADO: Determinando estado...")

        exp.save_results()

        print("\n4️⃣ REPLANTEO: Decisión basada en resultados...")

        state = exp.results["authentication_state"]

        if state == "AUTHENTICATED":
            print(f"""
🎉 **YA ESTAMOS AUTENTICADOS!**

👉 DECISIÓN: Saltar login, proceder con upload flow
   - Confianza: {exp.results['metrics'].get('auth_confidence', 0):.0f}%
   - Indicadores: {len(exp.results['indicators']['authenticated'])} a favor
   - Siguiente: EXP-003 - Navegación directa a /create""")

        elif state == "NOT_AUTHENTICATED":
            print(f"""
🔧 **NO ESTAMOS AUTENTICADOS**

👉 DECISIÓN: Proceder con login completo
   - Confianza: {exp.results['metrics'].get('auth_confidence', 0):.0f}%
   - Indicadores: {len(exp.results['indicators']['not_authenticated'])} en contra
   - Siguiente: EXP-003 - Login con credenciales""")

        else:
            print(f"""
⚠️ **ESTADO INDETERMINADO**

👉 DECISIÓN: Investigación adicional requerida
   - Confianza: {exp.results['metrics'].get('auth_confidence', 0):.0f}%
   - Evidencia conflictiva
   - Siguiente: EXP-002c - Análisis profundo""")

    except Exception as e:
        print(f"\n🚨 ERROR: {str(e)}")
        exp.results["errors"].append(str(e))
        exp.save_results()

    finally:
        if browser:
            await browser.close()
            await exp.playwright.stop()

        print(f"\n{'='*70}")
        print(f"🏁 CICLO EXP-002b COMPLETADO")
        print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())