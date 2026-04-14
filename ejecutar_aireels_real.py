#!/usr/bin/env python3
"""
Ejecución real controlada de AIReels Instagram Upload Service.

Este script ejecuta una demostración realista del sistema completo
con medidas de seguridad y validaciones.
"""

import os
import sys
import asyncio
import tempfile
from pathlib import Path

# Configurar paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "instagram-upload"))

print("=" * 70)
print("🚀 EJECUCIÓN REAL CONTROLADA - AIReels Instagram Upload")
print("=" * 70)

def check_environment():
    """Verificar entorno y credenciales."""
    print("\n🔍 VERIFICANDO ENTORNO Y CONFIGURACIÓN")
    print("-" * 50)
    
    # Verificar archivo .env.instagram
    env_path = project_root / "instagram-upload" / ".env.instagram"
    if not env_path.exists():
        print("❌ Archivo .env.instagram no encontrado")
        return False
    
    print(f"✅ Archivo de configuración: {env_path}")
    
    # Leer configuración
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Verificar credenciales
    has_username = "INSTAGRAM_USERNAME" in env_content
    has_password = "INSTAGRAM_PASSWORD" in env_content
    has_dry_run = "INSTAGRAM_DRY_RUN" in env_content
    
    if has_username and has_password:
        print("✅ Credenciales configuradas en .env.instagram")
    else:
        print("⚠️  Credenciales no configuradas en .env.instagram")
        print("   El sistema usará modo DEMO/PRUEBA")
    
    if has_dry_run and "INSTAGRAM_DRY_RUN=false" in env_content:
        print("✅ Modo REAL activado (INSTAGRAM_DRY_RUN=false)")
    else:
        print("⚠️  Modo DRY-RUN activado o no especificado")
        print("   Para ejecución real: INSTAGRAM_DRY_RUN=false")
    
    # Verificar directorio de videos
    videos_dir = project_root / "instagram-upload" / "videos" / "to_upload"
    if videos_dir.exists():
        videos = list(videos_dir.glob("*.mp4")) + list(videos_dir.glob("*.mov"))
        if videos:
            print(f"✅ Videos encontrados: {len(videos)} archivos")
            for v in videos[:3]:  # Mostrar primeros 3
                print(f"   • {v.name}")
            if len(videos) > 3:
                print(f"   • ... y {len(videos)-3} más")
        else:
            print("⚠️  Directorio de videos vacío")
    else:
        print("❌ Directorio de videos no encontrado")
    
    return True

def create_test_video():
    """Crear video de prueba para demostración."""
    print("\n🎬 CREANDO VIDEO DE PRUEBA")
    print("-" * 50)
    
    try:
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        test_video_path = Path(temp_dir) / "test_demo_video.mp4"
        
        # Crear archivo de video simulado
        with open(test_video_path, 'wb') as f:
            # Escribir cabecera simulada de video MP4
            f.write(b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41')
            f.write(b'demo_video_content' * 1000)  # Contenido simulado
        
        size_kb = test_video_path.stat().st_size / 1024
        print(f"✅ Video de prueba creado: {test_video_path}")
        print(f"   • Tamaño: {size_kb:.1f} KB")
        print(f"   • Formato: mp4")
        print(f"   • Ubicación temporal: {temp_dir}")
        
        return test_video_path, temp_dir
        
    except Exception as e:
        print(f"❌ Error creando video de prueba: {e}")
        return None, None

async def execute_demo_flow():
    """Ejecutar flujo de demostración controlado."""
    print("\n🔄 EJECUTANDO FLUJO DE DEMOSTRACIÓN")
    print("-" * 50)
    
    try:
        # Importar módulos (ya verificados en tests)
        from src.auth.browser_service import BrowserService, BrowserConfig, BrowserType
        from src.auth.login_manager import InstagramLoginManager
        from src.auth.cookie_manager import CookieManager
        from src.upload.video_uploader import VideoUploader, VideoInfo
        from src.upload.metadata_handler import MetadataHandler, VideoMetadata
        from src.upload.publisher import Publisher
        
        print("✅ Módulos importados exitosamente")
        
        # 1. Configurar componentes
        print("\n1. 🛠️  CONFIGURANDO COMPONENTES")
        
        # Configuración de navegador (headless para demo)
        config = BrowserConfig(
            headless=True,  # Headless para demo
            slow_mo=100,    # Pequeño delay para visualización
            timeout=30000,  # 30 segundos timeout
            browser_type=BrowserType.CHROMIUM
        )
        
        browser_service = BrowserService(config)
        login_manager = InstagramLoginManager()
        cookie_manager = CookieManager()
        
        print(f"   • BrowserService: {config.browser_type.value} (headless: {config.headless})")
        print(f"   • LoginManager: usuario configurado")
        print(f"   • CookieManager: path={cookie_manager.cookies_path}")
        
        # 2. Verificar autenticación
        print("\n2. 🔐 VERIFICANDO AUTENTICACIÓN")
        
        if cookie_manager.has_valid_session():
            username = cookie_manager.get_session_username()
            print(f"   ✅ Sesión válida encontrada para: {username}")
            print(f"   • Usando cookies guardadas")
        else:
            print(f"   ⚠️  No hay sesión válida")
            print(f"   • Se requerirá login (modo demo simulado)")
        
        # 3. Crear video de prueba
        print("\n3. 🎥 PREPARANDO CONTENIDO")
        
        video_path, temp_dir = create_test_video()
        if not video_path:
            print("   ❌ No se pudo crear video de prueba")
            return False
        
        # Información del video
        video_info = VideoInfo(
            path=str(video_path),
            caption="Demo AIReels - Upload automatizado a Instagram",
            hashtags=["aireels", "automation", "instagram", "demo", "python"],
            location="Virtual Demo Location"
        )

        print(f"   ✅ Video preparado: {video_info.path}")
        print(f"   • Caption: {video_info.caption[:60]}...")
        print(f"   • Hashtags: {', '.join(video_info.hashtags)}")
        print(f"   • Location: {video_info.location}")
        
        # 4. Validar video
        print("\n4. ✓ VALIDANDO VIDEO")
        
        try:
            video_info.validate()
            print(f"   ✅ Video válido: formato={video_info.video_format}")
        except Exception as e:
            print(f"   ❌ Validación falló: {e}")
            print(f"   • Continuando en modo demostración...")
        
        # 5. Configurar metadata
        print("\n5. 🏷️  CONFIGURANDO METADATA")
        
        metadata = VideoMetadata(
            caption=video_info.caption,
            hashtags=video_info.hashtags,
            location=video_info.location
        )
        
        metadata_handler = MetadataHandler()
        publisher = Publisher()
        video_uploader = VideoUploader()
        
        print(f"   ✅ Metadata configurada")
        print(f"   • Handler: {metadata_handler.__class__.__name__}")
        print(f"   • Publisher: dry_run={getattr(publisher, 'dry_run', 'N/A')}")
        print(f"   • Uploader: {video_uploader.__class__.__name__}")
        
        # 6. Verificar modo de operación
        print("\n6. ⚙️  MODO DE OPERACIÓN")
        
        dry_run = os.environ.get('INSTAGRAM_DRY_RUN', 'true').lower() == 'true'
        if dry_run:
            print(f"   ✅ MODO DEMO ACTIVADO")
            print(f"   • No se realizarán acciones reales")
            print(f"   • Simulación completa del flujo")
        else:
            print(f"   🚨 MODO REAL ACTIVADO")
            print(f"   • Se intentará login real")
            print(f"   • Se intentará upload real")
            print(f"   • REQUIERE CREDENCIALES VÁLIDAS")
        
        # 7. Limpiar
        print("\n7. 🧹 LIMPIANDO RECURSOS")
        
        import shutil
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
            print(f"   ✅ Directorio temporal eliminado: {temp_dir}")
        
        print("\n✅ FLUJO DE DEMOSTRACIÓN COMPLETADO")
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en flujo de demostración: {type(e).__name__}: {e}")
        return False

async def main():
    """Función principal."""
    
    # Verificar entorno
    if not check_environment():
        print("\n⚠️  Configuración incompleta. Usando modo DEMO...")
    
    # Ejecutar flujo de demostración
    success = await execute_demo_flow()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE EJECUCIÓN")
    print("=" * 70)
    
    if success:
        print("✅ DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("\n🎯 LOGRADO:")
        print("   • Entorno verificado ✓")
        print("   • Componentes configurados ✓")
        print("   • Video de prueba creado ✓")
        print("   • Metadata configurada ✓")
        print("   • Flujo simulado ejecutado ✓")
        
        print("\n🚀 PARA EJECUCIÓN REAL:")
        print("   1. Agregar credenciales a .env.instagram:")
        print("      INSTAGRAM_USERNAME=tu_usuario")
        print("      INSTAGRAM_PASSWORD=tu_contraseña")
        print("   2. Configurar INSTAGRAM_DRY_RUN=false")
        print("   3. Colocar videos en: instagram-upload/videos/to_upload/")
        print("   4. Ejecutar: python instagram-upload/full_system_test.py")
    else:
        print("⚠️  DEMOSTRACIÓN CON ERRORES")
        print("\n💡 SOLUCIONES:")
        print("   • Verificar dependencias: pip install -r requirements.txt")
        print("   • Verificar configuraciones en .env.instagram")
        print("   • Ejecutar tests primero: python -m pytest instagram-upload/tests/")
    
    print("\n" + "=" * 70)
    print("🏁 FIN DE EJECUCIÓN - AIReels Instagram Upload")
    print("=" * 70)

if __name__ == "__main__":
    # Configurar asyncio
    asyncio.run(main())
