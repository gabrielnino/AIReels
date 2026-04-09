#!/bin/bash
# Script de configuración para Instagram Upload Service
# Responsable: Main Developer
# Uso: ./scripts/setup_instagram_config.sh

set -e  # Exit on error

echo "🔧 Configuración de Instagram Upload Service"
echo "============================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "README.md" ]; then
    echo "❌ Error: Ejecutar desde directorio raíz de AIReels"
    exit 1
fi

# Crear estructura de directorios
echo "📁 Creando estructura de directorios..."
mkdir -p data logs videos/to_upload videos/processed videos/failed

# Verificar si ya existe .env.instagram
if [ -f ".env.instagram" ]; then
    echo "⚠️  Archivo .env.instagram ya existe"
    read -p "¿Sobrescribir? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "✅ Configuración existente preservada"
        exit 0
    fi
fi

# Crear archivo de configuración
echo "📝 Creando archivo de configuración..."
cp templates/.env.instagram.template .env.instagram

echo ""
echo "⚙️  Configuración requerida:"
echo "============================="
echo "1. Editar .env.instagram con credenciales reales"
echo "2. Completar INSTAGRAM_USERNAME y INSTAGRAM_PASSWORD"
echo "3. Configurar otras variables según necesidad"
echo ""
echo "🔐 Credenciales proporcionadas:"
echo "   Usuario: fiestacotoday"
echo "   Contraseña: [protegida]"
echo ""
echo "⚠️  ADVERTENCIAS DE SEGURIDAD:"
echo "==============================="
echo "❌ NUNCA commitar .env.instagram al repositorio"
echo "❌ NUNCA compartir credenciales por chat/email"
echo "❌ Usar variables de entorno en producción"
echo "✅ Rotar contraseñas regularmente"
echo "✅ Monitorear actividad de la cuenta"
echo ""
echo "🚀 Pasos siguientes:"
echo "==================="
echo "1. Editar .env.instagram:"
echo "   nano .env.instagram"
echo ""
echo "2. Instalar dependencias:"
echo "   pip install -r requirements.txt"
echo "   playwright install chromium"
echo ""
echo "3. Probar configuración:"
echo "   python scripts/test_instagram_login.py"
echo ""
echo "4. Ejecutar tests:"
echo "   pytest tests/instagram/ -v"
echo ""
echo "📋 Checklist de seguridad:"
echo "=========================="
echo "[ ] Cuenta de Instagram es Business/Creator"
echo "[ ] 2FA desactivado o manejado en código"
echo "[ ] Backup de cookies habilitado"
echo "[ ] Logs no contienen credenciales"
echo "[ ] Session timeout configurado"
echo ""

# Crear script de prueba de login
cat > scripts/test_instagram_login.py << 'EOF'
#!/usr/bin/env python3
"""
Script de prueba para login de Instagram con Playwright.
Solo para desarrollo - NO usar en producción sin revisión.
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar configuración
load_dotenv('.env.instagram')

async def test_instagram_login():
    """Prueba básica de login a Instagram."""
    from playwright.async_api import async_playwright

    print("🔐 Probando login de Instagram...")

    async with async_playwright() as p:
        # Configurar browser
        browser = await p.chromium.launch(
            headless=os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true',
            slow_mo=int(os.getenv('PLAYWRIGHT_SLOW_MO', '100'))
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = await context.new_page()

        try:
            # Navegar a Instagram
            print("🌐 Navegando a Instagram...")
            await page.goto('https://www.instagram.com/')
            await page.wait_for_timeout(2000)

            # Aceptar cookies si aparece
            try:
                accept_button = page.get_by_role("button", name="Allow all cookies")
                if await accept_button.is_visible(timeout=3000):
                    await accept_button.click()
                    print("✅ Cookies aceptadas")
                    await page.wait_for_timeout(1000)
            except:
                pass  # No hay popup de cookies

            # Ingresar credenciales
            print("📝 Ingresando credenciales...")
            username = os.getenv('INSTAGRAM_USERNAME')
            password = os.getenv('INSTAGRAM_PASSWORD')

            if not username or not password:
                print("❌ Credenciales no configuradas en .env.instagram")
                return False

            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)

            # Click en login
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)

            # Verificar login exitoso
            try:
                # Buscar elemento que indique login exitoso
                await page.wait_for_selector('svg[aria-label="Home"]', timeout=10000)
                print("✅ Login exitoso")

                # Guardar cookies para futuras sesiones
                cookies_path = os.getenv('INSTAGRAM_COOKIES_PATH', './data/instagram_cookies.json')
                Path(cookies_path).parent.mkdir(parents=True, exist_ok=True)

                cookies = await context.cookies()
                import json
                with open(cookies_path, 'w') as f:
                    json.dump(cookies, f)
                print(f"💾 Cookies guardadas en: {cookies_path}")

                return True

            except Exception as e:
                # Verificar si hay error de login
                error_text = await page.text_content('p[id="slfErrorAlert"]')
                if error_text:
                    print(f"❌ Error de login: {error_text}")
                else:
                    print(f"❌ Error desconocido: {e}")

                # Screenshot para debugging
                await page.screenshot(path='./logs/login_error.png')
                print("📸 Screenshot guardado en ./logs/login_error.png")

                return False

        except Exception as e:
            print(f"❌ Error durante login: {e}")
            return False

        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(test_instagram_login())
    if success:
        print("🎉 Prueba de login completada exitosamente")
    else:
        print("💀 Prueba de login falló")
        exit(1)
EOF

chmod +x scripts/test_instagram_login.py

echo "✅ Configuración completada"
echo "📄 Archivos creados:"
echo "   - .env.instagram (template)"
echo "   - scripts/test_instagram_login.py"
echo ""
echo "⚠️  IMPORTANTE: Completar las credenciales en .env.instagram antes de continuar"
echo "   Credenciales: fiestacotoday / [contraseña]"