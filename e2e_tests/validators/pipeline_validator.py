#!/usr/bin/env python3
"""
Validador para etapas del pipeline de generación de contenido.

Valida:
- Selección de tema (Trend Engine)
- Filtrado y scoring (Decision Engine)
- Definición de estrategia (Strategy Engine)
- Generación de contenido (Content Engine)

Created by: Sam Lead Developer
Date: 2026-04-10
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field

# Añadir ruta del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Intentar importar módulos de qwen-poc
try:
    from qwen_poc.pipeline import run_reels_pipeline
    HAS_QWEN_POC = True
except ImportError:
    HAS_QWEN_POC = False
    logging.warning("Módulo qwen-poc no disponible, usando mocks")


@dataclass
class PipelineValidationResult:
    """Resultado de validación del pipeline."""
    stage: str
    status: str  # passed | failed | warning
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class PipelineValidator:
    """Validador para etapas del pipeline de generación."""

    def __init__(self, config: Dict[str, Any]):
        """Inicializar validador de pipeline.

        Args:
            config: Configuración del sistema E2E
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuración específica del pipeline
        self.pipeline_config = config.get("pipeline", {})
        self.validation_config = config.get("validation", {})

        # Flags de validación por etapa
        self.stage_assertions = self.validation_config.get("stage_assertions", {})

    async def validate_topic_selection(self, mock_data: Optional[Dict] = None) -> PipelineValidationResult:
        """Validar etapa de selección de tema.

        Args:
            mock_data: Datos mock para testing (opcional)

        Returns:
            Resultado de validación
        """
        self.logger.info("🔍 Validando selección de tema...")

        result = PipelineValidationResult(
            stage="topic_selection",
            status="passed"
        )

        try:
            if mock_data:
                # Usar datos mock para testing
                candidate_topics = mock_data.get("candidate_topics", [])
                self.logger.info(f"Usando datos mock: {len(candidate_topics)} topics")

                # Validar estructura de datos mock
                validation_passed = self._validate_topic_structure(candidate_topics)

                if validation_passed:
                    result.details = {
                        "topics_count": len(candidate_topics),
                        "topics_sample": candidate_topics[:3] if candidate_topics else [],
                        "source": "mock_data"
                    }
                    result.metrics = {
                        "topics_generated": len(candidate_topics),
                        "validation_passed": True
                    }
                else:
                    result.status = "failed"
                    result.errors.append("Estructura inválida en datos mock de topics")

            elif HAS_QWEN_POC and self.pipeline_config.get("content_generation", True):
                # Ejecutar Trend Engine real (si está configurado)
                # Por ahora, usar implementación mock
                candidate_topics = await self._mock_trend_engine()

                result.details = {
                    "topics_count": len(candidate_topics),
                    "topics_sample": candidate_topics[:3] if candidate_topics else [],
                    "source": "mock_trend_engine"
                }
                result.metrics = {
                    "topics_generated": len(candidate_topics),
                    "validation_passed": True
                }

            else:
                # Modo sin generación real
                self.logger.info("Modo sin generación real - validación básica")
                result.details = {"mode": "no_generation"}
                result.metrics = {"validation_passed": True}

            # Aplicar assertions específicas
            if self.stage_assertions.get("topic_selection", True):
                assertion_result = self._apply_topic_selection_assertions(result)
                if not assertion_result["passed"]:
                    result.status = "failed"
                    result.errors.extend(assertion_result["errors"])

        except Exception as e:
            self.logger.error(f"Error validando selección de tema: {e}")
            result.status = "failed"
            result.errors.append(f"Error de validación: {str(e)}")

        self.logger.info(f"✅ Validación de selección de tema: {result.status}")
        return result

    async def validate_strategy_definition(self, topic_data: Optional[Dict] = None) -> PipelineValidationResult:
        """Validar etapa de definición de estrategia.

        Args:
            topic_data: Datos del tema seleccionado (opcional)

        Returns:
            Resultado de validación
        """
        self.logger.info("🔍 Validando definición de estrategia...")

        result = PipelineValidationResult(
            stage="strategy_definition",
            status="passed"
        )

        try:
            if topic_data:
                # Generar estrategia basada en topic
                strategy = await self._mock_strategy_engine(topic_data)

                result.details = {
                    "topic": topic_data.get("topic", "unknown"),
                    "strategy_components": list(strategy.keys()),
                    "emotion": strategy.get("emotion"),
                    "cta": strategy.get("cta"),
                    "source": "mock_strategy_engine"
                }
                result.metrics = {
                    "strategy_generated": True,
                    "components_count": len(strategy)
                }

            else:
                # Datos de ejemplo
                strategy = {
                    "emotion": "inspirational",
                    "cta": "Follow for more AI insights!",
                    "on_screen_text": "The future of AI is here",
                    "visual_style": "modern_tech",
                    "music_type": "upbeat_instrumental"
                }

                result.details = {
                    "strategy_sample": strategy,
                    "source": "example_data"
                }
                result.metrics = {
                    "strategy_generated": True,
                    "components_count": len(strategy)
                }

            # Aplicar assertions
            if self.stage_assertions.get("strategy_definition", True):
                assertion_result = self._apply_strategy_assertions(result)
                if not assertion_result["passed"]:
                    result.status = "failed"
                    result.errors.extend(assertion_result["errors"])

        except Exception as e:
            self.logger.error(f"Error validando definición de estrategia: {e}")
            result.status = "failed"
            result.errors.append(f"Error de validación: {str(e)}")

        self.logger.info(f"✅ Validación de definición de estrategia: {result.status}")
        return result

    async def validate_asset_generation(self, strategy_data: Optional[Dict] = None) -> PipelineValidationResult:
        """Validar etapa de generación de assets.

        Args:
            strategy_data: Datos de estrategia (opcional)

        Returns:
            Resultado de validación
        """
        self.logger.info("🔍 Validando generación de assets...")

        result = PipelineValidationResult(
            stage="asset_generation",
            status="passed"
        )

        try:
            # Simular generación de assets
            assets = await self._mock_asset_generation(strategy_data)

            result.details = {
                "assets_generated": list(assets.keys()),
                "images_count": len(assets.get("image_urls", [])),
                "has_audio": "audio_prompt" in assets,
                "has_video": "video_path" in assets,
                "source": "mock_asset_generation"
            }
            result.metrics = {
                "assets_count": len(assets),
                "images_generated": len(assets.get("image_urls", [])),
                "audio_generated": "audio_prompt" in assets,
                "video_generated": "video_path" in assets
            }

            # Aplicar assertions
            if self.stage_assertions.get("asset_generation", True):
                assertion_result = self._apply_asset_generation_assertions(result)
                if not assertion_result["passed"]:
                    result.status = "failed"
                    result.errors.extend(assertion_result["errors"])

        except Exception as e:
            self.logger.error(f"Error validando generación de assets: {e}")
            result.status = "failed"
            result.errors.append(f"Error de validación: {str(e)}")

        self.logger.info(f"✅ Validación de generación de assets: {result.status}")
        return result

    async def validate_complete_pipeline(self, execute_content: bool = True) -> PipelineValidationResult:
        """Validar pipeline completo.

        Args:
            execute_content: Si se debe ejecutar generación real de contenido

        Returns:
            Resultado de validación completa
        """
        self.logger.info("🔍 Validando pipeline completo...")

        result = PipelineValidationResult(
            stage="complete_pipeline",
            status="passed"
        )

        stages_results = []
        total_metrics = {}

        try:
            # 1. Validar selección de tema
            topic_result = await self.validate_topic_selection()
            stages_results.append(topic_result)

            if topic_result.status == "failed":
                result.status = "failed"
                result.errors.append("Fallo en selección de tema")
                return result

            # 2. Validar definición de estrategia
            # Usar datos mock del tema
            mock_topic = {"topic": "AI Technology", "score": 85}
            strategy_result = await self.validate_strategy_definition(mock_topic)
            stages_results.append(strategy_result)

            if strategy_result.status == "failed":
                result.status = "failed"
                result.errors.append("Fallo en definición de estrategia")
                return result

            # 3. Validar generación de assets (si está habilitado)
            if execute_content:
                asset_result = await self.validate_asset_generation()
                stages_results.append(asset_result)

                if asset_result.status == "failed":
                    result.status = "failed"
                    result.errors.append("Fallo en generación de assets")
                    return result

            # Consolidar resultados
            result.details = {
                "stages_executed": [r.stage for r in stages_results],
                "stages_passed": len([r for r in stages_results if r.status == "passed"]),
                "stages_failed": len([r for r in stages_results if r.status == "failed"]),
                "total_stages": len(stages_results)
            }

            # Consolidar métricas
            for stage_result in stages_results:
                for key, value in stage_result.metrics.items():
                    if key not in total_metrics:
                        total_metrics[key] = []
                    total_metrics[key].append(value)

            result.metrics = {
                "success_rate": (result.details["stages_passed"] / result.details["total_stages"]) * 100,
                "total_stages": result.details["total_stages"],
                "passed_stages": result.details["stages_passed"]
            }

        except Exception as e:
            self.logger.error(f"Error validando pipeline completo: {e}")
            result.status = "failed"
            result.errors.append(f"Error de validación: {str(e)}")

        self.logger.info(f"✅ Validación de pipeline completo: {result.status}")
        return result

    # Métodos de ayuda para mocking
    async def _mock_trend_engine(self) -> List[Dict[str, Any]]:
        """Simular Trend Engine."""
        await asyncio.sleep(0.1)  # Simular procesamiento

        return [
            {
                "topic": "AI Technology",
                "relevance_score": 92,
                "trend_score": 85,
                "search_volume": 15000,
                "category": "technology"
            },
            {
                "topic": "Machine Learning",
                "relevance_score": 88,
                "trend_score": 78,
                "search_volume": 12000,
                "category": "technology"
            },
            {
                "topic": "Future of Work",
                "relevance_score": 85,
                "trend_score": 82,
                "search_volume": 9500,
                "category": "business"
            }
        ]

    async def _mock_strategy_engine(self, topic_data: Dict) -> Dict[str, Any]:
        """Simular Strategy Engine."""
        await asyncio.sleep(0.1)

        topic = topic_data.get("topic", "AI Technology")

        return {
            "emotion": "inspirational",
            "cta": f"Learn more about {topic}!",
            "on_screen_text": f"The amazing world of {topic}",
            "visual_style": "modern_tech",
            "music_type": "upbeat_instrumental",
            "target_audience": "tech_enthusiasts",
            "key_message": f"{topic} is changing our world"
        }

    async def _mock_asset_generation(self, strategy_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Simular generación de assets."""
        await asyncio.sleep(0.2)

        return {
            "image_urls": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg",
                "https://example.com/image3.jpg"
            ],
            "audio_prompt": "An inspiring soundtrack about technology",
            "video_path": "/tmp/generated_video.mp4",
            "caption": "Discover the future of technology with AI!",
            "hashtags": ["AI", "Technology", "Future", "Innovation"],
            "metadata": {
                "duration_seconds": 30,
                "resolution": "1080x1920",
                "format": "mp4"
            }
        }

    # Métodos de validación
    def _validate_topic_structure(self, topics: List[Dict]) -> bool:
        """Validar estructura de datos de topics."""
        if not isinstance(topics, list):
            return False

        for topic in topics:
            if not isinstance(topic, dict):
                return False

            # Verificar campos mínimos
            if "topic" not in topic:
                return False

        return True

    def _apply_topic_selection_assertions(self, result: PipelineValidationResult) -> Dict[str, Any]:
        """Aplicar assertions para selección de tema."""
        errors = []
        passed = True

        details = result.details

        # Assertion 1: Debe haber al menos un topic
        if details.get("topics_count", 0) == 0:
            errors.append("No se generaron topics")
            passed = False

        # Assertion 2: Los topics deben tener estructura válida
        topics_sample = details.get("topics_sample", [])
        for topic in topics_sample:
            if not topic.get("topic"):
                errors.append(f"Topic sin campo 'topic': {topic}")
                passed = False

        # Assertion 3: Scores deben ser numéricos si existen
        for topic in topics_sample:
            if "relevance_score" in topic and not isinstance(topic["relevance_score"], (int, float)):
                errors.append(f"Score no numérico en topic: {topic}")
                passed = False

        return {"passed": passed, "errors": errors}

    def _apply_strategy_assertions(self, result: PipelineValidationResult) -> Dict[str, Any]:
        """Aplicar assertions para definición de estrategia."""
        errors = []
        passed = True

        details = result.details

        # Assertion 1: Debe tener emotion
        if not details.get("emotion"):
            errors.append("Estrategia sin emotion definida")
            passed = False

        # Assertion 2: Emotion debe ser válida
        valid_emotions = ["inspirational", "educational", "emotional", "funny", "informative"]
        emotion = details.get("emotion")
        if emotion and emotion not in valid_emotions:
            errors.append(f"Emotion no válida: {emotion}. Válidas: {valid_emotions}")
            passed = False

        # Assertion 3: Debe tener CTA
        if not details.get("cta"):
            errors.append("Estrategia sin CTA")
            passed = False

        return {"passed": passed, "errors": errors}

    def _apply_asset_generation_assertions(self, result: PipelineValidationResult) -> Dict[str, Any]:
        """Aplicar assertions para generación de assets."""
        errors = []
        passed = True

        details = result.details

        # Assertion 1: Debe generar imágenes
        if details.get("images_count", 0) < 1:
            errors.append("No se generaron imágenes")
            passed = False

        # Assertion 2: Número razonable de imágenes
        if details.get("images_count", 0) > 10:
            errors.append(f"Demasiadas imágenes generadas: {details['images_count']}")
            passed = False

        # Assertion 3: Debe tener metadata para video si aplica
        if details.get("has_video") and not details.get("video_metadata"):
            errors.append("Video generado sin metadata")
            passed = False

        return {"passed": passed, "errors": errors}

    # Métodos de utilidad
    def get_validation_summary(self, results: List[PipelineValidationResult]) -> Dict[str, Any]:
        """Obtener resumen de validaciones."""
        total = len(results)
        passed = len([r for r in results if r.status == "passed"])
        failed = len([r for r in results if r.status == "failed"])
        warnings = len([r for r in results if r.status == "warning"])

        all_errors = []
        all_warnings = []

        for result in results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)

        return {
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "errors": all_errors[:10],  # Limitar a 10 errores
            "warnings": all_warnings[:10]  # Limitar a 10 warnings
        }