#!/usr/bin/env python3
"""
Quick demo showing SUCCESSFUL pipeline execution.

This demonstrates a complete successful flow with proper hashtags
and disabled file validation for demonstration purposes.

Created by: Sam Lead Developer
Date: 2026-04-08
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from integration import (
    PipelineBridge,
    AlwaysSuccessUploader,
    UploadOptions,
)


def setup_logging():
    """Configure logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def create_valid_qwen_output() -> dict:
    """
    Create a VALID qwen-poc output for successful demo.
    """
    # Create a dummy file for the demo
    dummy_video = "/tmp/demo_video.mp4"
    if not os.path.exists(dummy_video):
        with open(dummy_video, 'wb') as f:
            # Write a small dummy MP4 header
            f.write(b'\x00\x00\x00\x1cftypmp42\x00\x00\x00\x00mp42mp41')

    return {
        "topic": "AI Transforming Content Creation",
        "emotion": "excited",
        "final_video_path": dummy_video,
        "caption": "AI is revolutionizing how we create content! From video editing to copywriting, AI tools are making creators more efficient. What's your favorite AI tool?",
        "hashtags": ["#ai", "#contentcreation", "#digitaltransformation", "#futureofwork"],
        "location": "Virtual",
        "cta": "Share your thoughts in the comments!",
        "on_screen_text": "AI = Amazing Innovation",
    }


async def run_successful_demo():
    """Run a successful demo from start to finish."""
    logger = setup_logging()

    print("🚀 **DEMOSTRACIÓN EXITOSA DEL PIPELINE**")
    print("=" * 60)

    # Step 1: Create uploader that ALWAYS succeeds
    logger.info("1. Creando uploader (AlwaysSuccessUploader)")
    uploader = AlwaysSuccessUploader(delay_seconds=2.0)

    # Step 2: Configure options (disable file validation for demo)
    logger.info("2. Configurando opciones de upload")
    options = UploadOptions(
        validate_video=False,  # Disable for demo
        validate_metadata=True,
        max_retries=2,
        retry_delay_seconds=1
    )

    # Step 3: Create pipeline bridge
    logger.info("3. Creando PipelineBridge")
    bridge = PipelineBridge(uploader, options)

    # Step 4: Create valid qwen-poc output
    logger.info("4. Generando output simulado de qwen-poc")
    qwen_output = create_valid_qwen_output()

    print("\n📊 **METADATA GENERADO:**")
    print(f"  Tópico: {qwen_output['topic']}")
    print(f"  Emoción: {qwen_output['emotion']}")
    print(f"  Video: {qwen_output['final_video_path']}")
    print(f"  Caption: {qwen_output['caption'][:80]}...")
    print(f"  Hashtags: {', '.join(qwen_output['hashtags'])}")

    # Step 5: Process and upload
    print("\n🔄 **EJECUTANDO PIPELINE COMPLETO:**")
    logger.info("5. Ejecutando pipeline completo (adaptación → validación → upload)")

    result = await bridge.process_and_upload(qwen_output, options)

    # Step 6: Show results
    print("\n✅ **RESULTADO FINAL:**")
    print(f"  Estado: {result.status.value.upper()}")
    print(f"  Media ID: {result.media_id}")
    print(f"  Duración total: {result.total_duration_seconds:.1f}s")
    print(f"  Duración upload: {result.upload_duration_seconds:.1f}s")

    if result.successful:
        print("\n🎉 **¡PIPELINE EXITOSO!**")
        print("El sistema funcionó perfectamente:")
        print("  1. ✅ Adaptación de metadata")
        print("  2. ✅ Validación de formatos")
        print("  3. ✅ Upload a Instagram (simulado)")
        print("  4. ✅ Retorno de resultados")
    else:
        print(f"\n❌ Error: {result.error_message}")

    # Show bridge info
    print("\n🏗️ **INFORMACIÓN DE ARQUITECTURA:**")
    bridge_info = bridge.get_bridge_info()
    print(f"  Versión: {bridge_info['bridge_version']}")
    print(f"  Uploader: {bridge_info['uploader']['name']}")
    print(f"  Capacidades: {', '.join(bridge_info['capabilities'].keys())}")

    print("\n" + "=" * 60)
    print("✨ **DEMOSTRACIÓN COMPLETADA CON ÉXITO**")

    return result


async def main():
    """Run the demo."""
    try:
        result = await run_successful_demo()
        return 0 if result.successful else 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)