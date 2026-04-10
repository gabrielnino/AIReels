# 🧪 ESTRATEGIA DE PRUEBAS END-TO-END (E2E) REALES

## 📋 ANÁLISIS COMPLETO DEL FLUJO

### **1. Pipeline qwen-poc (`qwen-poc/pipeline.py`)**
**Flujo identificado:**
```
run_reels_pipeline() → 
  init_db() → 
  run_trend_engine() → 
  run_decision_engine() → 
  run_strategy_engine() → 
  run_content_engine() → 
  upload_reel_to_instagram()
```

**Servicios involucrados (13 total):**
1. `trend_engine.py` - Búsqueda tendencias (Brave Search API)
2. `decision_engine.py` - Filtrado y scoring topics
3. `strategy_engine.py` - Definición estrategia contenido
4. `content_engine.py` - Orquestador generación assets
5. `search_service.py` - API Brave Search (1280 líneas)
6. `llm_service.py` - DeepSeek API (1518 líneas)
7. `image_service.py` - DashScope API (3525 líneas)
8. `audio_service.py` - Generación audio (2152 líneas)
9. `video_service.py` - FAL API (11671 líneas)
10. `voiceover_service.py` - ElevenLabs API (8464 líneas)
11. `subtitle_service.py` - Subtítulos (8370 líneas)
12. `endcard_service.py` - End cards (4114 líneas)
13. `instagram_service.py` - Graph API Instagram (9748 líneas)

### **2. Instagram Upload (`instagram-upload/`)**
**Dos enfoques identificados:**
- **Graph API:** `qwen-poc/service/instagram_service.py`
- **Playwright UI:** `instagram-upload/src/upload/`

### **3. Integration Bridge (`src/integration/`)**
**Propósito:** Puente entre qwen-poc output y upload systems
**Componentes clave:**
- `data_models.py` - Estructuras datos estandarizadas
- `metadata_adapter.py` - Conversión qwen-poc → Instagram format
- `pipeline_bridge.py` - Orquestación flujo completo
- `mock_uploader.py` - Sistema mocking para testing

---

## 🎯 PUNTOS DE VALIDACIÓN CRÍTICOS POR ETAPA

### **ETAPA 1: Selección del Tema**
**Validaciones:**
- ✅ **Input:** Parámetros ejecución (language, execute_content)
- ✅ **Output:** `candidate_topics` no vacío
- ✅ **Calidad:** Topics relevantes, actuales, diversos
- ✅ **Dependencias:** Brave Search API funcionando
- ✅ **Logging:** Registro de tendencias descubiertas

**Assertions:**
```python
assert len(candidate_topics) > 0, "No topics generated"
assert all('topic' in t for t in candidate_topics), "Invalid topic format"
assert all('relevance_score' in t for t in candidate_topics), "Missing scores"
```

### **ETAPA 2: Filtrado y Scoring**
**Validaciones:**
- ✅ **Input:** `candidate_topics` desde Trend Engine
- ✅ **Output:** `winning_topic_data` con metadata completa
- ✅ **Filtros:** Temas duplicados, calidad mínima, diversidad
- ✅ **Scoring:** Algoritmo consistente, pesos configurables
- ✅ **Memoria:** Evitar repetición temas recientes

**Assertions:**
```python
assert winning_topic_data is not None, "No winning topic selected"
assert 'topic' in winning_topic_data, "Missing topic in winning data"
assert 'reasoning' in winning_topic_data, "Missing selection reasoning"
assert 'score' in winning_topic_data, "Missing final score"
```

### **ETAPA 3: Estrategia de Contenido**
**Validaciones:**
- ✅ **Input:** `winning_topic_data` (tema seleccionado)
- ✅ **Output:** `strategy` dict con emociones, CTA, texto on-screen
- ✅ **Coherencia:** Estrategia alineada con tema y audiencia
- ✅ **Creatividad:** Variedad en enfoques (educativo, emocional, etc.)
- ✅ **LLM:** DeepSeek API funcionando, prompts efectivos

**Assertions:**
```python
assert 'emotion' in strategy, "Missing emotion in strategy"
assert 'cta' in strategy, "Missing CTA in strategy"
assert 'on_screen_text' in strategy, "Missing on-screen text"
assert strategy['emotion'] in ['inspirational', 'educational', 'emotional', 'funny']
```

### **ETAPA 4: Generación de Assets**
**Sub-etapas críticas:**

#### **4.1 Imágenes (DashScope API)**
**Validaciones:**
- ✅ **Cantidad:** 3-5 imágenes generadas
- ✅ **Formato:** JPEG/PNG, resolución mínima 1080x1920
- ✅ **Tamaño:** < 10MB por imagen
- ✅ **Relevancia:** Coherente con prompt y tema
- ✅ **Calidad:** Artefactos mínimos, colores vibrantes

#### **4.2 Audio (Voiceover + Música)**
**Validaciones:**
- ✅ **Duración:** 15-60 segundos (estándar Reels)
- ✅ **Formato:** MP3/WAV, calidad ≥ 128kbps
- ✅ **Sincronización:** Timing con imágenes
- ✅ **Voz:** Natural, emociones apropiadas
- ✅ **Música:** Volumen balanceado, sin copyright issues

#### **4.3 Video Final (FAL API)**
**Validaciones:**
- ✅ **Duración:** 15-60 segundos
- ✅ **Formato:** MP4, codec H.264, resolución 1080x1920
- ✅ **Tamaño:** < 100MB (límite Instagram)
- ✅ **FPS:** 30/60 fps consistente
- ✅ **Audio:** Sincronizado, niveles correctos
- ✅ **Subtítulos:** Precisos, timing correcto

**Assertions totales etapa:**
```python
assert os.path.exists(final_assets["silent_video_path"]), "Silent video missing"
assert os.path.exists(final_assets["video_with_audio_path"]), "Video with audio missing"
assert os.path.exists(final_assets["final_video_path"]), "Final video missing"
assert 15 <= get_video_duration(final_assets["final_video_path"]) <= 60, "Invalid duration"
assert get_video_size(final_assets["final_video_path"]) < 100 * 1024 * 1024, "File too large"
```

### **ETAPA 5: Publicación en Instagram**
**Validaciones:**
- ✅ **Metadata completa:** caption, hashtags, location, schedule
- ✅ **Límites Instagram:** 
  - Caption: ≤ 2200 caracteres
  - Hashtags: ≤ 30, relevantes
  - Video: ≤ 100MB, 15-60 segundos
- ✅ **Autenticación:** Tokens válidos, sesión activa
- ✅ **Upload:** Progreso monitorizado, timeouts manejados
- ✅ **Resultado:** Media ID, post URL, timestamps

**Assertions:**
```python
assert result['success'] == True, "Upload failed"
assert 'media_id' in result, "Missing media ID"
assert 'post_url' in result, "Missing post URL"
assert result['media_id'].startswith('179'), "Invalid Instagram media ID format"
```

### **ETAPA 6: Validación Post-Publicación**
**Validaciones:**
- ✅ **Publicación visible:** Post accesible via URL
- ✅ **Contenido correcto:** Video reproducido, calidad preservada
- ✅ **Metadata publicada:** Caption, hashtags coinciden
- ✅ **Engagement inicial:** Views > 0 después de publicación
- ✅ **Evidencia:** Screenshots, logs, IDs almacenados

**Assertions:**
```python
assert is_post_accessible(post_url), "Post not accessible"
assert get_post_caption(post_url) == expected_caption, "Caption mismatch"
assert get_post_hashtags(post_url) == expected_hashtags, "Hashtags mismatch"
assert get_post_video_url(post_url) is not None, "Video missing from post"
```

---

## 🚨 DEPENDENCIAS EXTERNAS Y RIESGOS

### **APIs Críticas:**
1. **Instagram Graph API**
   - Rate limits: 200 calls/hour
   - Video upload limit: 100MB
   - Requiere: Access token, página Instagram
   - Riesgo: Token expiry, rate limiting

2. **DashScope API (Alibaba Cloud)**
   - Rate limits: Dependen del plan
   - Costo: Por imagen generada
   - Requiere: API key, configuración modelo
   - Riesgo: Costos imprevistos, downtime

3. **DeepSeek API**
   - Rate limits: Modelo-specific
   - Contexto: 128K tokens
   - Requiere: API key
   - Riesgo: Response quality variability

4. **FAL API**
   - Rate limits: Dependen del plan
   - Video generation: Tiempo variable (segundos-minutos)
   - Requiere: API key, créditos
   - Riesgo: Generation failures, timeouts

5. **Brave Search API**
   - Rate limits: 20,000 searches/month (free)
   - Requiere: API key
   - Riesgo: Resultados inconsistentes, límites mensuales

6. **ElevenLabs API**
   - Rate limits: Caracteres/mes
   - Calidad voz: Premium required para mejor calidad
   - Requiere: API key
   - Riesgo: Costos por uso, calidad variable

### **Riesgos Operacionales:**
1. **Costos imprevistos:** APIs con pricing por uso
2. **Rate limiting:** Bloqueos temporales por exceso de requests
3. **Downtime APIs:** Servicios externos no disponibles
4. **Cambios APIs:** Breaking changes sin aviso
5. **Calidad variable:** Outputs inconsistentes entre ejecuciones

---

## 🛡️ ESTRATEGIA DE MITIGACIÓN

### **1. Entornos de Prueba**
- **Development:** Mock completo de todas las APIs
- **Staging:** APIs reales con límites estrictos
- **Production-like:** Entorno aislado con cuenta Instagram de prueba

### **2. Mecanismos de Recovery**
- **Retry con backoff exponencial:** Para errores temporales
- **Fallbacks:** Modelos alternativos si API primaria falla
- **Circuit breakers:** Detener llamadas si API consistently failing
- **Queue persistente:** Reprocesamiento manual si necesario

### **3. Monitoreo y Alertas**
- **Health checks:** APIs externas antes de ejecución
- **Budget alerts:** Uso aproximado de APIs pagadas
- **Rate limit tracking:** % usado de quotas
- **Performance metrics:** Tiempos por etapa, success rates

### **4. Limpieza Automática**
- **Publicaciones de prueba:** Eliminar después de validación
- **Archivos temporales:** Limpiar después de ejecución
- **Logs sensibles:** Sanitizar antes de almacenamiento
- **Credenciales:** Rotación automática si comprometidas

---

## 📊 CASOS DE PRUEBA E2E DEFINIDOS

### **Caso 1: Flujo Básico Exitoso**
**Objetivo:** Validar pipeline completo con datos reales
**Pre-condiciones:**
- Todas las APIs configuradas con credenciales válidas
- Cuenta Instagram de prueba disponible
- Entorno aislado para pruebas reales

**Pasos:**
1. Ejecutar `run_reels_pipeline(execute_content=True)`
2. Validar selección tema (assert: topic ≠ None)
3. Validar generación imágenes (assert: 3-5 imágenes, formato correcto)
4. Validar generación video (assert: video 15-60s, <100MB)
5. Validar publicación Instagram (assert: media_id, post_url)
6. Validar post-publicación (assert: post accesible, metadata correcta)
7. Limpieza: Eliminar publicación de prueba

**Métricas de éxito:**
- Tiempo total < 30 minutos
- Todas las assertions pasan
- Evidencia completa recopilada

### **Caso 2: Recuperación de Errores**
**Objetivo:** Validar mecanismos de recovery
**Pre-condiciones:**
- API DashScope simulada para fallar en primer intento
- Instagram Graph API con rate limit simulado

**Pasos:**
1. Ejecutar pipeline con API failures simulados
2. Validar retry mechanism (assert: retry con backoff)
3. Validar fallback si aplicable (assert: alternative model usado)
4. Validar graceful degradation (assert: error manejado, logs claros)
5. Validar cleanup después de fallo (assert: recursos liberados)

**Métricas de éxito:**
- Error manejado apropiadamente
- No data corruption
- Logs informativos para debugging

### **Caso 3: Validación de Límites**
**Objetivo:** Validar handling de edge cases
**Pre-condiciones:**
- Video de 120 segundos (excede límite Instagram)
- Caption de 3000 caracteres (excede límite)
- 40 hashtags (excede límite)

**Pasos:**
1. Ejecutar pipeline con inputs extremos
2. Validar trimming automático (assert: caption ≤ 2200 chars)
3. Validar compresión video (assert: video ≤ 60s, ≤ 100MB)
4. Validar límite hashtags (assert: ≤ 30 hashtags)
5. Validar publicación exitosa aún con ajustes

**Métricas de éxito:**
- Ajustes automáticos aplicados
- Publicación exitosa con contenido válido
- Logs documentando ajustes aplicados

### **Caso 4: Performance y Escalabilidad**
**Objetivo:** Validar performance bajo carga
**Pre-condiciones:**
- Pipeline configurado para ejecución paralela
- APIs con rate limits conocidos

**Pasos:**
1. Ejecutar 3 pipelines en paralelo
2. Medir tiempos por etapa
3. Validar no exceder rate limits
4. Validar isolation entre ejecuciones
5. Validar cleanup concurrente

**Métricas de éxito:**
- No rate limiting violations
- Tiempos consistentes
- Recursos adecuadamente aislados

---

## 🛠️ HERRAMIENTAS Y CONFIGURACIÓN

### **1. Entorno de Pruebas**
```yaml
environment:
  name: "e2e-testing"
  mode: "production-like"
  isolation_level: "full"  # full | partial | none
  
apis:
  instagram:
    account_type: "test"  # test | real
    dry_run: false
    validation_timeout: 300  # segundos
    
  ai_services:
    mock_mode: "partial"  # full | partial | none
    rate_limit_simulation: true
    budget_alerts_enabled: true
    
logging:
  level: "DEBUG"
  evidence_collection: "full"  # full | partial | none
  screenshot_on_failure: true
  log_retention_days: 7
```

### **2. Configuración de Seguridad**
```yaml
security:
  credential_storage: "env_vars"  # env_vars | vault | aws_secrets
  credential_rotation: "weekly"
  
  data_sanitization:
    enabled: true
    sanitize_fields: ["api_keys", "tokens", "passwords"]
    
  network_isolation:
    enabled: true
    allowed_endpoints_only: true
```

### **3. Herramientas de Validación**
- **Video validation:** `ffprobe` (duración, codec, resolución)
- **Image validation:** `PIL/Pillow` (formato, tamaño, resolución)
- **Audio validation:** `pydub` (duración, codec, bitrate)
- **Instagram validation:** Graph API endpoints + Playwright scraping
- **Performance monitoring:** `time`, `memory_profiler`, `psutil`

### **4. Evidencia y Reportes**
- **Screenshots:** Playwright para capturas post-publicación
- **Logs estructurados:** JSON logs con contexto por etapa
- **Artifacts:** Videos, imágenes, metadata almacenados
- **Reportes:** HTML/PDF con timeline, assertions, evidencias
- **Dashboards:** Métricas en tiempo real durante ejecución

---

## 📈 MÉTRICAS DE ÉXITO Y CRITERIOS DE ACEPTACIÓN

### **Métricas Cuantitativas:**
1. **Success rate:** ≥ 90% de pruebas E2E pasan
2. **Execution time:** ≤ 30 minutos por prueba completa
3. **Resource usage:** CPU < 80%, RAM < 4GB durante ejecución
4. **API costs:** ≤ $5 por prueba completa (estimado)
5. **Evidence coverage:** 100% de etapas con logs + artifacts

### **Métricas Cualitativas:**
1. **Stability:** Ejecución predecible y reproducible
2. **Recovery:** Graceful degradation en fallos
3. **Documentation:** Reportes claros y accionables
4. **Maintainability:** Código de pruebas modular y reutilizable
5. **Security:** Credenciales protegidas, datos sanitizados

### **Criterios de Aceptación:**
1. ✅ Pipeline ejecuta sin intervención manual
2. ✅ Publicación real ocurre en Instagram (o dry_run verificado)
3. ✅ Validación post-publicación confirma éxito
4. ✅ Evidencia completa recopilada y almacenada
5. ✅ Reporte claro generado automáticamente
6. ✅ Recursos limpiados apropiadamente
7. ✅ Código documentado y mantenible

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### **Fase 1: Diseño y Preparación (4 horas)**
1. **Análisis código fuente completo** (2 horas)
   - Mapear TODOS los puntos de integración
   - Documentar TODAS las dependencias externas
   - Identificar TODOS los posibles failure points

2. **Diseño arquitectura pruebas** (1 hora)
   - Definir estructura `e2e_tests/` directory
   - Diseñar interfaces de validación por etapa
   - Planificar mecanismos de logging y evidence

3. **Configuración entorno** (1 hora)
   - Setup entorno aislado para pruebas
   - Configurar credenciales de prueba seguras
   - Establecer mecanismos de cleanup automático

### **Fase 2: Implementación Core (8 horas)**
1. **Test runner E2E** (2 horas)
   - `e2e_test_runner.py` - Orquestador principal
   - `test_scenarios.py` - Escenarios predefinidos
   - `test_orchestrator.py` - Gestión múltiples tests

2. **Validators por etapa** (3 horas)
   - `pipeline_validator.py` - Validación pipeline qwen-poc
   - `asset_validator.py` - Validación imágenes/video/audio
   - `metadata_validator.py` - Validación caption/hashtags

3. **Instagram publisher real** (2 horas)
   - `instagram_publisher_e2e.py` - Publicación real
   - `dry_run_publisher.py` - Modo seguro para testing
   - `credential_manager.py` - Gestión segura credenciales

4. **Post-publication validator** (1 hora)
   - `post_publication_validator.py` - Verificación post-upload
   - `evidence_collector.py` - Recolección screenshots/logs
   - `report_generator.py` - Generación reportes

### **Fase 3: Integración y Validación (4 horas)**
1. **Ejecución pruebas piloto** (2 horas)
   - Pruebas con mocking completo
   - Pruebas con APIs reales (modo controlado)
   - Validación end-to-end completa

2. **Refinamiento y ajustes** (1 hora)
   - Ajustar timeouts y retry logic
   - Mejorar logging y evidence collection
   - Optimizar performance y resource usage

3. **Documentación y handoff** (1 hora)
   - Documentar casos de prueba
   - Crear guías de ejecución
   - Establecer proceso de mantenimiento

### **Timeline Total:** 16 horas de desarrollo
### **Equipo requerido:** 5 miembros (40 horas-persona total)

---

## 🔄 INTEGRACIÓN CON SISTEMA EXISTENTE

### **1. Con qwen-poc:**
```python
# Hook en pipeline existente para validación
from e2e_tests.validators.pipeline_validator import PipelineValidator

validator = PipelineValidator()
pipeline_result = run_reels_pipeline(execute_content=True)
validation_result = validator.validate_pipeline_output(pipeline_result)
```

### **2. Con instagram-upload:**
```python
# Wrapper alrededor de uploader existente
from e2e_tests.publishers.instagram_publisher_e2e import InstagramPublisherE2E
from instagram_upload.src.upload.publisher import Publisher

publisher = InstagramPublisherE2E(
    wrapped_publisher=Publisher(),
    validation_mode="full"
)
result = publisher.upload_video_with_validation(metadata)
```

### **3. Con integration module:**
```python
# Extensión del bridge existente
from src.integration.pipeline_bridge import PipelineBridge
from e2e_tests.e2e_pipeline_bridge import E2EPipelineBridge

# Bridge extendido con validación E2E
bridge = E2EPipelineBridge(uploader)
result = bridge.run_pipeline_with_validation(qwen_output)
```

---

## 📝 PRÓXIMOS PASOS INMEDIATOS

### **Inmediato (hoy):**
1. ✅ Actualizar `E2E_TESTING_PLAN.md` con análisis completo
2. ✅ Crear `E2E_TESTING_STRATEGY.md` detallado
3. ✅ Definir estructura de directorios `e2e_tests/`
4. ✅ Documentar API dependencies y rate limits

### **Corto plazo (1-2 días):**
1. Implementar `e2e_test_runner.py` básico
2. Configurar entorno de pruebas seguro
3. Crear primeros validators (pipeline, assets)
4. Ejecutar prueba piloto con mocking completo

### **Medio plazo (3-5 días):**
1. Implementar publicación real con Instagram
2. Desarrollar validación post-publicación
3. Crear sistema de evidence collection
4. Ejecutar primera prueba E2E completa

### **Largo plazo (1 semana):**
1. Integrar en CI/CD pipeline
2. Automatizar ejecución regular
3. Implementar dashboards de métricas
4. Documentar procesos operativos

---

## 🏁 CONCLUSIÓN

Esta planeación proporciona una **estrategia completa y accionable** para pruebas E2E que:

1. **Cubre el flujo completo** desde selección tema hasta validación post-publicación
2. **Identifica puntos críticos de validación** en cada etapa del pipeline
3. **Documenta dependencias externas** y estrategias de mitigación
4. **Define casos de prueba específicos** con criterios de aceptación claros
5. **Propone herramientas y configuración** para implementación efectiva
6. **Establece timeline realista** con asignación de equipo

**Próxima acción recomendada:** Comenzar implementación con Fase 1 (Diseño y Preparación) según timeline propuesto.

**Responsable:** Equipo completo coordinado por Casey Code Refactoring Expert
**Timeline:** 16 horas de desarrollo distribuido en 5 días
**Entregable:** Sistema de pruebas E2E completamente funcional con validación automatizada