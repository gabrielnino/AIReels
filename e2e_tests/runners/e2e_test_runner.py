#!/usr/bin/env python3
"""
Runner principal para pruebas End-to-End (E2E).

Orquesta el flujo completo de pruebas E2E, gestionando:
- Configuración del entorno
- Ejecución secuencial de etapas
- Manejo de errores y recovery
- Generación de reportes

Created by: Casey Code Refactoring Expert
Date: 2026-04-10
"""

import os
import sys
import time
import logging
import asyncio
import yaml
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field

# Añadir ruta del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from e2e_tests.validators.pipeline_validator import PipelineValidator
from e2e_tests.validators.asset_validator import AssetValidator
from e2e_tests.validators.metadata_validator import MetadataValidator
from e2e_tests.publishers.instagram_publisher_e2e import InstagramPublisherE2E
from e2e_tests.validators.post_publication_validator import PostPublicationValidator
from e2e_tests.collectors.evidence_collector import EvidenceCollector
from e2e_tests.utils.report_generator import ReportGenerator


@dataclass
class E2ETestResult:
    """Resultado de una prueba E2E."""
    test_id: str
    scenario_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending | running | completed | failed | skipped
    stages: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def add_stage(self, stage_name: str, status: str, duration: float,
                  details: Dict[str, Any] = None):
        """Añadir resultado de una etapa."""
        stage_result = {
            "name": stage_name,
            "status": status,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.stages.append(stage_result)

    def add_error(self, error: str, stage: str = None):
        """Añadir error."""
        error_entry = {
            "message": error,
            "stage": stage,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error_entry)

    def add_warning(self, warning: str, stage: str = None):
        """Añadir warning."""
        warning_entry = {
            "message": warning,
            "stage": stage,
            "timestamp": datetime.now().isoformat()
        }
        self.warnings.append(warning_entry)

    def calculate_metrics(self):
        """Calcular métricas finales."""
        if not self.end_time:
            self.end_time = datetime.now()

        total_duration = (self.end_time - self.start_time).total_seconds()

        self.metrics = {
            "total_duration": total_duration,
            "stages_count": len(self.stages),
            "stages_passed": len([s for s in self.stages if s["status"] == "completed"]),
            "stages_failed": len([s for s in self.stages if s["status"] == "failed"]),
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "success_rate": (len([s for s in self.stages if s["status"] == "completed"]) /
                           max(1, len(self.stages))) * 100
        }


class E2ETestRunner:
    """Runner principal para pruebas E2E."""

    def __init__(self, config_path: str = "e2e_config.yaml"):
        """Inicializar runner E2E.

        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.test_id = self._generate_test_id()
        self.result = None

        # Inicializar componentes
        self.validators = {}
        self.publisher = None
        self.collector = None
        self.reporter = None

        # Setup logging
        self._setup_logging()

    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo YAML."""
        config_path = Path(self.config_path)

        if not config_path.exists():
            logging.warning(f"Archivo de configuración no encontrado: {config_path}")
            logging.info("Usando configuración por defecto")
            return self._get_default_config()

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            logging.info(f"Configuración cargada desde: {config_path}")
            return config

        except Exception as e:
            logging.error(f"Error cargando configuración: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Obtener configuración por defecto."""
        return {
            "environment": {
                "mode": "development",
                "use_real_apis": False,
                "global_timeout": 1800
            },
            "validation": {
                "stage_assertions": {
                    "topic_selection": True,
                    "strategy_definition": True,
                    "asset_generation": True,
                    "metadata_validation": True,
                    "publication_process": True,
                    "post_publication": True
                }
            }
        }

    def _generate_test_id(self) -> str:
        """Generar ID único para la prueba."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"e2e_test_{timestamp}"

    def _setup_logging(self):
        """Configurar sistema de logging."""
        log_level = self.config.get("reporting", {}).get("log_level", "INFO").upper()

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"e2e_tests/reports/logs/{self.test_id}.log")
            ]
        )

        self.logger = logging.getLogger(__name__)

    def _initialize_components(self):
        """Inicializar todos los componentes necesarios."""
        self.logger.info("🧩 Inicializando componentes E2E...")

        try:
            # Inicializar validators
            self.validators["pipeline"] = PipelineValidator(self.config)
            self.validators["assets"] = AssetValidator(self.config)
            self.validators["metadata"] = MetadataValidator(self.config)
            self.validators["post_publication"] = PostPublicationValidator(self.config)

            # Inicializar publisher
            self.publisher = InstagramPublisherE2E(self.config)

            # Inicializar collector
            self.collector = EvidenceCollector(self.config, self.test_id)

            # Inicializar reporter
            self.reporter = ReportGenerator(self.config, self.test_id)

            self.logger.info("✅ Componentes inicializados exitosamente")

        except Exception as e:
            self.logger.error(f"❌ Error inicializando componentes: {e}")
            raise

    async def run_stage(self, stage_name: str, stage_func, *args, **kwargs) -> Dict[str, Any]:
        """Ejecutar una etapa del pipeline.

        Args:
            stage_name: Nombre de la etapa
            stage_func: Función a ejecutar
            *args, **kwargs: Argumentos para la función

        Returns:
            Resultado de la etapa
        """
        self.logger.info(f"🚀 Ejecutando etapa: {stage_name}")
        stage_start = time.time()

        try:
            # Ejecutar etapa
            result = await stage_func(*args, **kwargs)
            duration = time.time() - stage_start

            if result.get("status") == "completed":
                self.logger.info(f"✅ Etapa completada: {stage_name} ({duration:.2f}s)")
                return {
                    "status": "completed",
                    "duration": duration,
                    "result": result,
                    "error": None
                }
            else:
                self.logger.warning(f"⚠️ Etapa con advertencias: {stage_name} ({duration:.2f}s)")
                return {
                    "status": "warning",
                    "duration": duration,
                    "result": result,
                    "error": result.get("error")
                }

        except Exception as e:
            duration = time.time() - stage_start
            self.logger.error(f"❌ Error en etapa {stage_name}: {e}")

            # Capturar evidencia del error si es posible
            if self.collector:
                await self.collector.capture_error(stage_name, str(e))

            return {
                "status": "failed",
                "duration": duration,
                "result": None,
                "error": str(e)
            }

    async def run_pipeline_stage(self, stage_name: str) -> Dict[str, Any]:
        """Ejecutar etapa específica del pipeline.

        Args:
            stage_name: Nombre de la etapa del pipeline

        Returns:
            Resultado de la etapa
        """
        # Este método será implementado según la etapa específica
        # Por ahora es un placeholder
        return {"status": "completed", "message": f"Stage {stage_name} executed"}

    async def run_test_scenario(self, scenario_name: str = "basic_success") -> E2ETestResult:
        """Ejecutar un escenario de prueba completo.

        Args:
            scenario_name: Nombre del escenario a ejecutar

        Returns:
            Resultado de la prueba
        """
        self.logger.info(f"🧪 INICIANDO PRUEBA E2E: {scenario_name}")
        self.logger.info(f"📋 Test ID: {self.test_id}")

        # Inicializar resultado
        self.result = E2ETestResult(
            test_id=self.test_id,
            scenario_name=scenario_name,
            start_time=datetime.now()
        )
        self.result.status = "running"

        # Inicializar componentes
        self._initialize_components()

        # Ejecutar etapas del pipeline
        stages = [
            ("topic_selection", "Selección de tema"),
            ("strategy_definition", "Definición de estrategia"),
            ("asset_generation", "Generación de assets"),
            ("metadata_validation", "Validación de metadata"),
            ("publication_process", "Proceso de publicación"),
            ("post_publication", "Validación post-publicación")
        ]

        for stage_key, stage_name in stages:
            # Verificar si la etapa está habilitada
            if not self.config.get("validation", {}).get("stage_assertions", {}).get(stage_key, True):
                self.logger.info(f"⏭️ Etapa saltada: {stage_name}")
                self.result.add_stage(stage_name, "skipped", 0.0)
                continue

            # Ejecutar etapa
            stage_result = await self.run_stage(
                stage_name,
                self.run_pipeline_stage,
                stage_key
            )

            # Registrar resultado
            self.result.add_stage(
                stage_name,
                stage_result["status"],
                stage_result["duration"],
                {"result": stage_result.get("result")}
            )

            # Manejar errores
            if stage_result["status"] == "failed":
                error_msg = f"Error en etapa {stage_name}: {stage_result['error']}"
                self.result.add_error(error_msg, stage_name)

                # Verificar si continuar según configuración
                if not self.config.get("recovery", {}).get("continue_on_stage_failure", True):
                    self.logger.error(f"❌ Deteniendo prueba por error en etapa: {stage_name}")
                    break

            elif stage_result["status"] == "warning":
                warning_msg = f"Advertencia en etapa {stage_name}: {stage_result.get('error')}"
                self.result.add_warning(warning_msg, stage_name)

        # Finalizar prueba
        self.result.status = "completed" if not self.result.errors else "failed"
        self.result.end_time = datetime.now()
        self.result.calculate_metrics()

        # Recopilar evidencia final
        if self.collector:
            await self.collector.finalize_collection(self.result)

        # Generar reporte
        if self.reporter:
            report_path = await self.reporter.generate_report(self.result)
            self.logger.info(f"📄 Reporte generado: {report_path}")

        # Mostrar resumen
        self._print_summary()

        return self.result

    def _print_summary(self):
        """Imprimir resumen de la prueba."""
        if not self.result:
            return

        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBA E2E")
        print("=" * 60)
        print(f"Test ID: {self.result.test_id}")
        print(f"Escenario: {self.result.scenario_name}")
        print(f"Estado: {self.result.status}")
        print(f"Duración total: {self.result.metrics.get('total_duration', 0):.2f}s")
        print(f"Etapas: {self.result.metrics.get('stages_passed', 0)}/{self.result.metrics.get('stages_count', 0)} pasadas")
        print(f"Errores: {self.result.metrics.get('errors_count', 0)}")
        print(f"Advertencias: {self.result.metrics.get('warnings_count', 0)}")
        print(f"Tasa de éxito: {self.result.metrics.get('success_rate', 0):.1f}%")

        if self.result.errors:
            print("\n❌ ERRORES:")
            for error in self.result.errors[:3]:  # Mostrar solo primeros 3
                print(f"  • {error.get('stage')}: {error.get('message')}")
            if len(self.result.errors) > 3:
                print(f"  ... y {len(self.result.errors) - 3} errores más")

        print("=" * 60)

    async def cleanup(self):
        """Realizar limpieza después de la prueba."""
        self.logger.info("🧹 Realizando limpieza...")

        try:
            # Limpiar publicaciones de prueba si existen
            if self.publisher:
                await self.publisher.cleanup_test_posts()

            # Limpiar archivos temporales
            if self.collector:
                await self.collector.cleanup_temporary_files()

            self.logger.info("✅ Limpieza completada")

        except Exception as e:
            self.logger.warning(f"⚠️ Error durante limpieza: {e}")


async def main():
    """Función principal para ejecutar runner E2E."""
    import argparse

    parser = argparse.ArgumentParser(description="Runner de pruebas E2E para AIReels")
    parser.add_argument("--config", "-c", default="e2e_config.yaml",
                       help="Ruta al archivo de configuración")
    parser.add_argument("--scenario", "-s", default="basic_success",
                       help="Escenario de prueba a ejecutar")
    parser.add_argument("--cleanup", action="store_true",
                       help="Realizar limpieza después de la prueba")

    args = parser.parse_args()

    # Crear runner
    runner = E2ETestRunner(args.config)

    try:
        # Ejecutar prueba
        result = await runner.run_test_scenario(args.scenario)

        # Realizar limpieza si se solicita
        if args.cleanup:
            await runner.cleanup()

        # Retornar código de salida según resultado
        if result.status == "completed":
            print("🎉 ¡PRUEBA E2E COMPLETADA EXITOSAMENTE!")
            sys.exit(0)
        else:
            print("❌ PRUEBA E2E FALLIDA")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ Prueba interrumpida por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error no manejado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())