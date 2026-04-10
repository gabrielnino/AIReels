# 🧪 PLAN DE PRUEBAS END-TO-END (E2E) REALES

**Objetivo:** Validar el flujo completo de publicación en Instagram de punta a punta con ejecución real (no mocks)

## 🎯 ALCANCE DE LAS PRUEBAS E2E

### **Flujo completo a validar:**
1. ✅ **Selección del tema** - Input inicial del contenido
2. ✅ **Generación de imágenes** - Basadas en el tema seleccionado  
3. ✅ **Generación del video final** - Ensamblaje y audio (si aplica)
4. ✅ **Publicación automática en Instagram** - Incluyendo:
   - Descripción (caption)
   - Hashtags relevantes
5. ✅ **Validación post-publicación** - Asegurar que:
   - El video fue publicado correctamente
   - El contenido (video, caption, hashtags) coincide con lo esperado

## 📋 REQUISITOS

### **Técnicos:**
- ✅ Entorno lo más cercano posible a producción (no mocks)
- ✅ Generación de datos reales y ejecución de acciones reales
- ✅ Mecanismos de verificación automática (assertions) en cada etapa crítica
- ✅ Registro de logs detallados y evidencia
  - IDs de publicación
  - URLs  
  - Capturas de pantalla (si es posible)

### **Operacionales:**
- ✅ Ejecución sin intervención manual
- ✅ Recuperación ante fallos
- ✅ Limpieza automática de recursos de prueba
- ✅ Reportes claros de resultados

## 🏗️ ARQUITECTURA DE PRUEBAS E2E

### **Componentes principales:**
1. **Test Runner E2E** - Orquestador de pruebas
2. **Monitor de Estado** - Seguimiento en tiempo real
3. **Validador de Resultados** - Verificación post-publicación
4. **Recolector de Evidencia** - Logs, screenshots, métricas

### **Flujo de ejecución:**
```
┌─────────────────────────────────────────────────────────────┐
│                    INICIO PRUEBA E2E                        │
├─────────────────────────────────────────────────────────────┤
│ 1. Configuración inicial (entorno, credenciales, limpieza)  │
│ 2. Ejecución pipeline completo (qwen-poc)                   │
│ 3. Validación de assets generados (imágenes, video, audio) │
│ 4. Publicación en Instagram (instagram-upload)             │
│ 5. Verificación post-publicación                           │
│ 6. Recopilación de evidencia                               │
│ 7. Limpieza y reporte final                                │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 COMPONENTES A IMPLEMENTAR

### **1. Test Runner E2E (`e2e_test_runner.py`)**
```python
class E2ETestRunner:
    """
    Orquestador principal de pruebas E2E.
    Gestiona el flujo completo y la coordinación entre componentes.
    """
    - Configuración de entorno
    - Ejecución secuencial/pasos
    - Manejo de errores y recovery
    - Generación de reportes
```

### **2. Validador de Pipeline (`pipeline_validator.py`)**
```python
class PipelineValidator:
    """
    Valida cada etapa del pipeline de generación.
    """
    - Validación de tema seleccionado
    - Verificación de assets generados
    - Comprobación de metadata
    - Validación de formato y tamaño
```

### **3. Publicador de Instagram (`instagram_publisher_e2e.py`)**
```python
class InstagramPublisherE2E:
    """
    Maneja la publicación real en Instagram.
    """
    - Autenticación real (no mocks)
    - Upload de video real
    - Configuración de caption y hashtags
    - Captura de IDs y URLs de publicación
```

### **4. Validador Post-Publicación (`post_publication_validator.py`)**
```python
class PostPublicationValidator:
    """
    Verifica que la publicación sea correcta después de subir.
    """
    - Verificación de publicación visible
    - Validación de caption y hashtags
    - Comprobación de video reproducido
    - Captura de screenshots de evidencia
```

### **5. Recolector de Evidencia (`evidence_collector.py`)**
```python
class EvidenceCollector:
    """
    Recopila y organiza toda la evidencia de la prueba.
    """
    - Logs estructurados
    - Screenshots (si es posible)
    - IDs y URLs de publicación
    - Métricas de performance
    - Archivos generados
```

## 📁 ESTRUCTURA DE ARCHIVOS

```
e2e_tests/
├── runners/
│   ├── e2e_test_runner.py          # Orquestador principal
│   ├── test_scenarios.py           # Escenarios de prueba predefinidos
│   └── test_orchestrator.py        # Gestión de múltiples tests
├── validators/
│   ├── pipeline_validator.py       # Validación pipeline
│   ├── asset_validator.py          # Validación assets
│   └── post_publication_validator.py # Validación post-upload
├── publishers/
│   ├── instagram_publisher_e2e.py  # Publicación real
│   └── dry_run_publisher.py        # Modo seguro para testing
├── collectors/
│   ├── evidence_collector.py       # Recolección de evidencia
│   ├── screenshot_capturer.py      # Captura de pantallas
│   └── log_aggregator.py           # Agregación de logs
├── utils/
│   ├── config_manager.py           # Gestión de configuración
│   ├── cleanup_manager.py          # Limpieza de recursos
│   └── report_generator.py         # Generación de reportes
├── scenarios/
│   ├── basic_flow_scenario.py      # Flujo básico
│   ├── error_recovery_scenario.py  # Pruebas de recuperación
│   └── performance_scenario.py     # Pruebas de performance
└── reports/
    ├── templates/                  # Plantillas de reportes
    └── historical/                 # Reportes históricos
```

## 🔧 CONFIGURACIÓN

### **Archivo de configuración (`e2e_config.yaml`):**
```yaml
environment:
  mode: "production_like"  # production_like | staging | development
  use_real_apis: true
  enable_screenshots: false  # Requiere configuración adicional
  
instagram:
  account_type: "test_account"  # test_account | real_account
  use_dry_run: false  # Para pruebas iniciales
  validation_timeout: 300  # segundos para validar publicación
  
pipeline:
  language: "en"
  max_execution_time: 1800  # 30 minutos máximo
  topic_override: null  # Forzar tema específico (opcional)
  
validation:
  check_video_playback: true
  verify_caption_content: true
  validate_hashtags: true
  screenshot_on_failure: true
  
reporting:
  generate_html_report: true
  save_evidence: true
  evidence_retention_days: 7
```

## 🧪 ESCENARIOS DE PRUEBA

### **Escenario 1: Flujo básico exitoso**
```python
def test_basic_successful_flow():
    """
    Flujo completo exitoso con verificación en cada etapa.
    """
    1. Seleccionar tema automáticamente
    2. Generar imágenes y video
    3. Publicar en Instagram
    4. Validar publicación exitosa
    5. Recopilar evidencia
```

### **Escenario 2: Recuperación de errores**
```python
def test_error_recovery_flow():
    """
    Prueba de recuperación ante fallos en diferentes etapas.
    """
    1. Simular fallo en generación de imágenes
    2. Verificar recovery mechanism
    3. Continuar con flujo alternativo
    4. Validar publicación final
```

### **Escenario 3: Validación de contenido**
```python
def test_content_validation_flow():
    """
    Validación exhaustiva de contenido generado.
    """
    1. Verificar coherencia tema → imágenes → video
    2. Validar calidad de caption y hashtags
    3. Comprobar metadatos completos
    4. Asegurar cumplimiento de políticas
```

### **Escenario 4: Performance y límites**
```python
def test_performance_boundaries():
    """
    Pruebas de límites y performance.
    """
    1. Tiempos de ejecución por etapa
    2. Uso de recursos (CPU, memoria, disco)
    3. Límites de tamaño de archivos
    4. Tiempos de timeout y recovery
```

## 🚀 PLAN DE IMPLEMENTACIÓN

### **Fase 1: Diseño y preparación (2 horas)**
- ✅ Crear estructura de directorios
- ✅ Definir interfaces y contratos
- ✅ Configurar entorno de pruebas
- ✅ Establecer mecanismos de logging

### **Fase 2: Implementación core (4 horas)**
- ✅ `e2e_test_runner.py` - Orquestador principal
- ✅ `pipeline_validator.py` - Validación de pipeline
- ✅ Configuración y manejo de credenciales
- ✅ Mecanismos básicos de recovery

### **Fase 3: Publicación real (3 horas)**
- ✅ `instagram_publisher_e2e.py` - Integración real
- ✅ Manejo de autenticación real (cookies/tokens)
- ✅ Upload real de videos
- ✅ Captura de IDs de publicación

### **Fase 4: Validación post-publicación (3 horas)**
- ✅ `post_publication_validator.py` - Verificación post-upload
- ✅ Mecanismos de polling/verificación
- ✅ Captura de evidencia (screenshots si es posible)
- ✅ Validación de contenido publicado

### **Fase 5: Reportes y mejoras (2 horas)**
- ✅ `evidence_collector.py` - Recolección estructurada
- ✅ Generación de reportes HTML/PDF
- ✅ Mejoras de logging y debugging
- ✅ Documentación de resultados

## 📊 MÉTRICAS DE ÉXITO

### **Métricas cuantitativas:**
- ✅ **Tasa de éxito:** > 90% de pruebas pasan
- ✅ **Tiempo de ejecución:** < 30 minutos por prueba completa
- ✅ **Cobertura:** 100% de etapas del flujo validadas
- ✅ **Evidencia:** Logs + IDs + URLs en 100% de pruebas

### **Métricas cualitativas:**
- ✅ **Fiabilidad:** Ejecución estable y predecible
- ✅ **Mantenibilidad:** Código claro y documentado
- ✅ **Recuperación:** Graceful degradation en fallos
- ✅ **Reportes:** Información clara y accionable

## 🚨 GESTIÓN DE RIESGOS

### **Riesgo 1: Publicaciones reales no deseadas**
- **Mitigación:** Usar cuenta de prueba dedicada
- **Mitigación:** Implementar `dry_run` mode inicial
- **Mitigación:** Limpieza automática post-prueba

### **Riesgo 2: Límites de API y rate limiting**
- **Mitigación:** Throttling inteligente
- **Mitigación:** Reintentos con backoff exponencial
- **Mitigación:** Monitoreo de quotas

### **Riesgo 3: Dependencias externas inestables**
- **Mitigación:** Timeouts configurados
- **Mitigación:** Fallback mechanisms
- **Mitigación:** Pruebas de connectivity pre-ejecución

### **Riesgo 4: Datos sensibles en logs**
- **Mitigación:** Sanitización automática
- **Mitigación:** Logging condicional por nivel
- **Mitigación:** Almacenamiento seguro de credenciales

## 📝 CRITERIOS DE ACEPTACIÓN

### **Pruebas E2E consideradas completas cuando:**
1. ✅ Flujo completo ejecuta sin intervención manual
2. ✅ Publicación real ocurre en Instagram (o dry_run verificado)
3. ✅ Validación post-publicación confirma éxito
4. ✅ Evidencia completa recopilada y almacenada
5. ✅ Reporte claro generado automáticamente
6. ✅ Recursos limpiados apropiadamente
7. ✅ Código documentado y mantenible

## 🔄 INTEGRACIÓN CON SISTEMA EXISTENTE

### **Integración con qwen-poc:**
```python
# Usar pipeline existente pero con hooks de validación
from qwen_poc.pipeline import run_reels_pipeline
from e2e_tests.validators.pipeline_validator import PipelineValidator

validator = PipelineValidator()
pipeline_result = run_reels_pipeline(execute_content=True)
validator.validate_pipeline_output(pipeline_result)
```

### **Integración con instagram-upload:**
```python
# Usar módulos existentes pero con wrappers de validación
from instagram_upload.src.upload.publisher import Publisher
from e2e_tests.publishers.instagram_publisher_e2e import InstagramPublisherE2E

publisher = InstagramPublisherE2E(wrapped_publisher=Publisher())
result = publisher.upload_video_with_validation(metadata)
```

## ✅ ANÁLISIS COMPLETADO

### **Fase de análisis finalizada (2026-04-10):**
1. ✅ **Código fuente analizado completamente:**
   - `qwen-poc/pipeline.py` y 13 servicios relacionados
   - `instagram-upload/src/upload/` y módulos de autenticación
   - `src/integration/` bridge entre sistemas
   
2. ✅ **Puntos de validación identificados:** 6 etapas críticas con assertions específicas
3. ✅ **Dependencias externas mapeadas:** 6 APIs críticas con rate limits y riesgos documentados
4. ✅ **Casos de prueba definidos:** 4 escenarios E2E con criterios de aceptación
5. ✅ **Estrategia de mitigación diseñada:** Entornos, recovery, monitoreo, limpieza
6. ✅ **Plan de implementación detallado:** 16 horas, 3 fases, asignación de equipo

### **Documentación generada:**
- ✅ `E2E_TESTING_STRATEGY.md` - Análisis completo y plan detallado
- ✅ Actualizado `TEAM_TASK_UPDATES.md` - Progreso del equipo documentado

## 🚀 PRÓXIMOS PASOS (IMPLEMENTACIÓN)

### **Fase 1: Diseño y Preparación (4 horas)**
1. **Análisis código fuente completo** (COMPLETADO ✅)
2. **Diseño arquitectura pruebas** - Definir estructura `e2e_tests/`
3. **Configuración entorno** - Setup entorno aislado para pruebas

### **Fase 2: Implementación Core (8 horas)**
1. **Test runner E2E** - `e2e_test_runner.py`, `test_scenarios.py`
2. **Validators por etapa** - pipeline, assets, metadata validators
3. **Instagram publisher real** - publicación real + dry_run mode
4. **Post-publication validator** - verificación post-upload

### **Fase 3: Integración y Validación (4 horas)**
1. **Ejecución pruebas piloto** - mocking completo → APIs reales
2. **Refinamiento y ajustes** - timeouts, logging, performance
3. **Documentación y handoff** - guías, procesos operativos

### **Timeline Total:** 16 horas de desarrollo (5 miembros, 40 horas-persona)

---

**🎯 OBJETIVO FINAL:** Pruebas E2E que validen el flujo completo de publicación en Instagram con ejecución real y verificación automática.

**📅 Timeline estimado:** 12-14 horas de desarrollo

---
*Generado para implementación de pruebas E2E reales - 2026-04-10*