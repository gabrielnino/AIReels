#!/usr/bin/env python3
"""
🚀 EXP-004: Enfoque directo a upload
Ciclo: IMPLEMENTACIÓN → PRUEBA → RESULTADO → REPLANTEO

ENFOQUE: Intentar upload directamente, manejando cualquier estado de autenticación
Basado en: EXP-001 (navegación funciona), EXP-003 (problema one-tap)
"""

import asyncio
import time
import os
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("🚀 EXP-004: ENFOQUE DIRECTO A UPLOAD")
print("=" * 70)
print("📋 Estrategia: Intentar upload manejando cualquier estado de autenticación")
print("   - Si ya autenticados: Navegar directamente a /create")
print("   - Si no autenticados: Intentar flujo simplificado")
print("   - Si bloqueado: Documentar y replantear")

async def direct_upload_experiment():
    """Experimento de upload directo."""
    from playwright.async_api import async_playwright

    results = {
        "experiment_id": "exp_004",
        "start_time": time.time(),
        "success": False,
        "state": "UNKNOWN",
        "steps": [],
        "errors": [],
        "screenshots": [],
        "video_found": False
    }

    # Crear directorio
    exp_dir = Path("experiments/exp_004")
    exp_dir.mkdir(exist_ok=True)

    playwright = None
    browser = None
    page = None

    try:
        print("\n1️⃣ IMPLEMENTACIÓN: Configuración directa...")

        # Configuración mínima probada en EXP-001
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,  # Visible para debugging
            slow_mo=800,     # Comportamiento humano
            args=['--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = await context.new_page()
        page.set_default_timeout(30000)

        results["steps"].append("browser_configured")

        print("\n2️⃣ PRUEBA REAL: Ejecutando flujo directo...")

        # Paso 1: Navegar a Instagram
        print("   🌐 Navegando a Instagram...")
        await page.goto('https://www.instagram.com/', wait_until='networkidle')
        await asyncio.sleep(2)

        initial_url = page.url
        print(f"   📍 URL inicial: {initial_url}")

        await page.screenshot(path=str(exp_dir / "01_initial.png"))
        results["screenshots"].append("01_initial.png")
        results["steps"].append("instagram_loaded")

        # Paso 2: Determinar estado de autenticación
        print("   🔍 Determinando estado de autenticación...")

        # Check rápido de indicadores
        auth_indicators = {
            "home_icon": await page.locator('svg[aria-label="Home"]').count() > 0,
            "create_icon": await page.locator('svg[aria-label="New post"]').count() > 0,
            "login_form": 'login' in initial_url or 'accounts/login' in initial_url,
            "onetap_page": 'onetap' in initial_url
        }

        print(f"   📊 Indicadores: Home={auth_indicators['home_icon']}, "
              f"Create={auth_indicators['create_icon']}, "
              f"OneTap={auth_indicators['onetap_page']}")

        # Determinar estado
        if auth_indicators['home_icon'] and auth_indicators['create_icon']:
            results["state"] = "AUTHENTICATED"
            print("   ✅ Estado: APARENTEMENTE AUTENTICADO")
        elif auth_indicators['onetap_page']:
            results["state"] = "ONETAP_FLOW"
            print("   ⚠️  Estado: EN FLUJO ONE-TAP (detectado en EXP-003)")
        elif auth_indicators['login_form']:
            results["state"] = "NOT_AUTHENTICATED"
            print("   ❌ Estado: NO AUTENTICADO")
        else:
            results["state"] = "UNKNOWN"
            print("   ❓ Estado: INDETERMINADO")

        results["steps"].append(f"state_determined_{results['state']}")

        # Paso 3: Intentar navegar directamente a /create
        print("   🎯 Intentando navegar directamente a página de upload...")

        # URLs de upload a probar (ordenadas por probabilidad)
        upload_urls = [
            "https://www.instagram.com/create",
            "https://www.instagram.com/create/",
            "https://www.instagram.com/create/select/",
            "https://www.instagram.com/create/select",  # Sin slash
        ]

        upload_success = False
        final_url = ""

        for url in upload_urls:
            print(f"   🔗 Probando: {url}")
            try:
                await page.goto(url, wait_until='networkidle', timeout=15000)
                await asyncio.sleep(3)

                current_url = page.url
                page_title = await page.title()

                print(f"   📍 URL actual: {current_url}")
                print(f"   📄 Título: {page_title}")

                # Verificar si estamos en página de upload
                if any(indicator in current_url.lower() for indicator in ['create', 'select']):
                    print(f"   ✅ POSIBLE ÉXITO: En página de upload ({url})")
                    await page.screenshot(path=str(exp_dir / f"02_upload_page_{url.split('/')[-1]}.png"))
                    results["screenshots"].append(f"02_upload_page_{url.split('/')[-1]}.png")
                    upload_success = True
                    final_url = current_url
                    break
                else:
                    print(f"   ⚠️  No parece página de upload")
                    await page.screenshot(path=str(exp_dir / f"02_not_upload_{url.split('/')[-1]}.png"))
                    results["screenshots"].append(f"02_not_upload_{url.split('/')[-1]}.png")

            except Exception as e:
                print(f"   ❌ Error navegando a {url}: {str(e)}")
                continue

        if not upload_success:
            print("   ❌ Todas las URLs de upload fallaron")
            results["errors"].append("No se pudo navegar a página de upload")
            results["steps"].append("upload_navigation_failed")
        else:
            print(f"   ✅ Navegación a upload exitosa: {final_url}")
            results["steps"].append("upload_navigation_success")

        # Paso 4: Verificar elementos de página de upload
        if upload_success:
            print("   🔎 Verificando elementos de página de upload...")

            upload_elements = {
                "create_button": await page.locator('div[role="button"]:has-text("Create")').count() > 0,
                "post_option": await page.locator('div[role="button"]:has-text("Post")').count() > 0,
                "story_option": await page.locator('div[role="button"]:has-text("Story")').count() > 0,
                "reel_option": await page.locator('div[role="button"]:has-text("Reel")').count() > 0,
                "upload_area": await page.locator('input[type="file"]').count() > 0 or
                             await page.locator('div[role="button"]:has-text("Select")').count() > 0
            }

            print(f"   📋 Elementos encontrados:")
            for element, found in upload_elements.items():
                print(f"     - {element}: {'✅' if found else '❌'}")

            if upload_elements["create_button"] or upload_elements["upload_area"]:
                print("   ✅ Elementos clave de upload detectados")
                results["steps"].append("upload_elements_found")

                # Capturar screenshot detallado
                await page.screenshot(path=str(exp_dir / "03_upload_elements.png"), full_page=True)
                results["screenshots"].append("03_upload_elements.png")

                # Paso 5: Verificar si hay video para upload
                print("   🎥 Verificando video disponible...")

                videos_dir = Path(__file__).parent.parent.parent / "instagram-upload" / "videos" / "to_upload"
                videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))

                if videos:
                    video_path = videos[0]
                    print(f"   ✅ Video encontrado: {video_path.name} ({video_path.stat().st_size / 1024:.1f} KB)")
                    results["video_found"] = True
                    results["steps"].append(f"video_found_{video_path.name}")

                    # NOTA: No intentamos upload automático en este experimento
                    # Solo verificamos que el flujo es posible
                    print("   📝 NOTA: Solo verificación, no upload real en este experimento")

                else:
                    print("   ⚠️  No hay videos en directorio de upload")
                    results["errors"].append("No hay videos para upload")
            else:
                print("   ❌ No se encontraron elementos clave de upload")
                results["errors"].append("Elementos de upload no encontrados")
                await page.screenshot(path=str(exp_dir / "03_no_upload_elements.png"), full_page=True)
                results["screenshots"].append("03_no_upload_elements.png")

        # Paso 6: Evaluar resultado general
        print("\n3️⃣ RESULTADO: Evaluando viabilidad...")

        # Criterios de éxito para este experimento
        success_criteria = {
            "upload_page_accessible": upload_success,
            "upload_elements_present": upload_success and any([
                upload_elements.get("create_button", False),
                upload_elements.get("upload_area", False)
            ]),
            "video_available": results["video_found"],
            "no_critical_errors": len([e for e in results["errors"] if "crítico" in e.lower()]) == 0
        }

        print(f"   📊 Criterios de éxito:")
        for criterion, met in success_criteria.items():
            print(f"     - {criterion}: {'✅' if met else '❌'}")

        # Determinar éxito general
        critical_success = success_criteria["upload_page_accessible"] and success_criteria["upload_elements_present"]
        partial_success = success_criteria["upload_page_accessible"] and not success_criteria["upload_elements_present"]

        if critical_success:
            results["success"] = True
            print("   🎉 ÉXITO CRÍTICO: Página de upload accesible con elementos")
        elif partial_success:
            results["success"] = "PARTIAL"
            print("   ⚠️  ÉXITO PARCIAL: Página accesible pero elementos incompletos")
        else:
            results["success"] = False
            print("   ❌ FALLO: Página de upload no accesible")

        # Generar reporte
        duration = time.time() - results["start_time"]
        results["duration"] = duration

        report = f"""# 🚀 EXP-004: Enfoque directo a upload

## 📊 RESULTADOS
{'✅' if results['success'] == True else '⚠️' if results['success'] == 'PARTIAL' else '❌'} **Estado:** {'EXITOSO' if results['success'] == True else 'PARCIALMENTE EXITOSO' if results['success'] == 'PARTIAL' else 'FALLIDO'}
⏱️ **Duración:** {duration:.1f} segundos
🔐 **Estado detectado:** {results['state']}
📸 **Screenshots:** {len(results['screenshots'])}
🚨 **Errores:** {len(results['errors'])}
📋 **Pasos:** {len(results['steps'])}
🎥 **Video disponible:** {'✅ Sí' if results['video_found'] else '❌ No'}

## 🎯 OBJETIVO
Probar navegación directa a página de upload, manejando cualquier estado de autenticación.

## 📈 DATOS CLAVE
- **URL inicial:** {initial_url}
- **Estado autenticación:** {results['state']}
- **Página upload accesible:** {'✅ Sí' if upload_success else '❌ No'}
- **Elementos upload encontrados:** {'✅ Sí' if success_criteria['upload_elements_present'] else '❌ No'}

## 📋 PASOS EJECUTADOS
"""
        for i, step in enumerate(results["steps"][:10], 1):
            report += f"{i}. {step}\n"

        if results["errors"]:
            report += "\n## 🚨 ERRORES\n"
            for error in results["errors"]:
                report += f"- {error}\n"

        if results["screenshots"]:
            report += "\n## 📸 EVIDENCIA VISUAL\n"
            for screenshot in results["screenshots"][:5]:  # Mostrar solo primeras 5
                report += f"![{screenshot}]({screenshot})\n"

        # Conclusión y siguiente paso
        report += f"""
## 🎯 CONCLUSIÓN
"""

        if results["success"] == True:
            report += """**✅ UPLOAD VIABLE DETECTADO**
- Página de upload accesible directamente
- Elementos clave presentes
- Video disponible para upload
- **¡Listo para intentar upload real!**"""
            next_exp = "EXP-005: Upload real de video"
            next_hypothesis = "Podemos subir video exitosamente"

        elif results["success"] == "PARTIAL":
            report += """**⚠️ PROGRESO PARCIAL**
- Página de upload accesible
- Pero elementos clave faltantes o incompletos
- Necesita investigación adicional"""
            next_exp = "EXP-004b: Investigar elementos faltantes"
            next_hypothesis = "Elementos de upload requieren interacción específica"

        else:
            report += """**❌ UPLOAD NO VIABLE DIRECTO**
- Página de upload no accesible
- Estado de autenticación problemático: """ + results["state"]
            if results["state"] == "ONETAP_FLOW":
                report += "\n- **Problema crítico:** Flujo one-tap bloqueando (detectado en EXP-003)"
                next_exp = "EXP-004b: Manejar flujo one-tap"
                next_hypothesis = "One-tap requiere intervención específica"
            else:
                next_exp = "EXP-004b: Debug profundo de navegación"
                next_hypothesis = "Problema específico en navegación a upload"

        report += f"""
## 📝 SIGUIENTE EXPERIMENTO
**{next_exp}**
- Objetivo: {'Realizar upload real' if results['success'] == True else 'Resolver bloqueos identificados'}
- Hipótesis: {next_hypothesis}

## 💡 RECOMENDACIÓN INMEDIATA
"""
        if results["success"] == True:
            report += "**¡EJECUTAR UPLOAD REAL AHORA!**\n- Usar video encontrado\n- Implementar selección de archivo\n- Probar publicación completa"
        elif results["state"] == "ONETAP_FLOW":
            report += "**INVESTIGAR FLUJO ONE-TAP**\n1. Analizar página /accounts/onetap/\n2. Identificar botones/interacciones requeridas\n3. Implementar manejo automático"
        else:
            report += "**DEBUG DETALLADO REQUERIDO**\n1. Revisar screenshots\n2. Identificar elementos bloqueantes\n3. Probar alternativas"

        report += f"""
---
*Ejecutado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Basado en aprendizajes de EXP-001 a EXP-003*
"""

        # Guardar reporte
        report_path = exp_dir / "results.md"
        report_path.write_text(report)

        print(f"\n📄 Reporte guardado en: {report_path}")

        print("\n4️⃣ REPLANTEO: Decisión estratégica...")

        if results["success"] == True:
            print(f"""
🎉 **¡UPLOAD VIABLE DETECTADO!**

👉 DECISIÓN: Proceder con UPLOAD REAL INMEDIATO
   - Página upload: ✅ Accesible
   - Elementos: ✅ Presentes
   - Video: ✅ Disponible
   - Siguiente: EXP-005 - Upload real con video""")

        elif results["state"] == "ONETAP_FLOW":
            print(f"""
🔧 **BLOQUEADO POR ONE-TAP (mismo problema que EXP-003)**

👉 DECISIÓN: Enfocar en resolver one-tap
   - Estado: {results['state']}
   - Problema: Flujo especial de Instagram
   - Siguiente: EXP-004b - Manejar /accounts/onetap/""")

        else:
            print(f"""
⚠️ **PROBLEMA NO RESUELTO**

👉 DECISIÓN: Investigación específica requerida
   - Estado: {results['state']}
   - Problema: {results['errors'][0] if results['errors'] else 'Desconocido'}
   - Siguiente: EXP-004b - Debug profundo""")

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
    print("📝 Este experimento prueba si podemos acceder directamente a upload")
    print("   sin resolver completamente el problema de login/one-tap")

    success = await direct_upload_experiment()

    print(f"\n{'='*70}")
    print(f"🏁 EXP-004 {'COMPLETADO - UPLOAD VIABLE' if success == True else 'PARCIAL - INVESTIGACIÓN REQUERIDA' if success == 'PARTIAL' else 'FALLÓ - BLOQUEOS IDENTIFICADOS'}")
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())