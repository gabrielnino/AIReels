# 📋 LISTA DE TAREAS CONCRETAS PARA TESTS Y DOCUMENTACIÓN

**Fecha:** 2026-04-09  
**Estado:** 🟡 PLANIFICACIÓN  
**Objetivo:** Tener lista de tactions específicas y medibles

---

## 🎯 **OBJETIVO FINAL**
Tener **100% cobertura de tests unitarios** y **documentación completa** para todo el proyecto AIReels.

---

## 📊 **ESTADO ACTUAL (VERIFICADO)**

### **✅ Lo que ya tenemos:**
1. **Módulo de integración:** 10 tests pytest, 100% pasan
2. **instagram-upload:** 6 unit tests + 2 integration tests
3. **qwen-poc:** 7 test files (funcionales más que unitarios)
4. **Documentación de proceso:** Completa (10+ archivos .md)
5. **Docstrings:** Parciales en algunos módulos

### **❌ Lo que falta (estimado):**
1. **~80 tests unitarios** adicionales
2. **~40 docstrings completos** adicionales
3. **5 READMEs** específicos por módulo
4. **15 tests E2E/integration** adicionales
5. **Configuración CI/CD** para tests automáticos

---

## 📝 **TAREAS POR MÓDULO (ORDEN DE PRIORIDAD)**

### **MÓDULO 1: qwen-poc (PRIORIDAD #1)**

#### **Tarea Q1: Setup testing infrastructure**
- **Descripción:** Configurar pytest, coverage reporting, mocking para qwen-poc
- **Archivos:** `qwen-poc/tests/`, `qwen-poc/requirements_test.txt`
- **Estimación:** 2 horas
- **Resultado:** `python3 -m pytest qwen-poc/tests/` ejecuta todos los tests

#### **Tarea Q2: Tests unitarios para servicios (15 servicios)**
**Sub-tareas por servicio:**

##### **Q2.1: service/llm_service.py**
- Tests para: `generate_strategy()`, `generate_script()`, `generate_image_prompts()`
- Mock: DeepSeek API calls
- Estimación: 1.5 horas

##### **Q2.2: service/search_service.py**
- Tests para: `search()`, `fetch_trending_queries()`
- Mock: Web scraping/responses
- Estimación: 1 hora

##### **Q2.3: service/image_service.py**
- Tests para: `generate_images()`, `generate_image()`
- Mock: DashScope API calls
- Estimación: 1.5 horas

##### **Q2.4: service/video_service.py**
- Tests para: `generate_video()`, `create_video_from_images()`
- Mock: FAL client, file operations
- Estimación: 2 horas

##### **Q2.5: service/audio_service.py**
- Tests para: `mix_voice_and_music()`, `create_audio_clip()`
- Mock: Audio file operations
- Estimación: 1 hora

##### **Q2.6: service/voiceover_service.py**
- Tests para: `generate_voiceover()`, `synthesize_speech()`
- Mock: Voice synthesis APIs
- Estimación: 1 hora

##### **Q2.7: service/subtitle_service.py**
- Tests para: `add_word_by_word_subtitles()`, `create_subtitle_file()`
- Mock: Video file operations
- Estimación: 1 hora

##### **Q2.8: service/endcard_service.py**
- Tests para: `add_endcard()`, `create_endcard_image()`
- Mock: Image generation, video editing
- Estimación: 1 hora

##### **Q2.9: service/instagram_service.py**
- Tests para: `upload_video()`, `validate_video()`
- Mock: Instagram Graph API
- Estimación: 1.5 horas

##### **Q2.10: service/ai_content_director.py**
- Tests para: `direct_content_creation()`, `create_content_plan()`
- Mock: LLM calls
- Estimación: 1.5 horas

##### **Q2.11: service/script_service.py**
- Tests para: `create_script()`, `format_script()`
- Mock: LLM calls
- Estimación: 1 hora

##### **Q2.12: service/fal_client.py**
- Tests para: `generate_video()`, `get_status()`
- Mock: FAL API calls
- Estimación: 1 hora

##### **Q2.13: service/lyria_service.ru**
- Tests para: `generate_lyria_music()`, `lyria_to_wav()`
- Mock: Lyria API calls
- Estimación: 1 hora

#### **Tarea Q3: Tests unitarios para engines (5 engines)**

##### **Q3.1: engine/trend_engine.py**
- Tests para: `run_trend_engine()`, `fetch_search_trends()`
- Estimación: 1.5 horas

##### **Q3.2: engine/strategy_engine.py**
- Tests para: `run_strategy_engine()`, `generate_content_strategy()`
- Estimación: 1.5 horas

##### **Q3.3: engine/content_engine.py**
- Tests para: `run_content_engine()`, `generate_full_content()`
- Estimación: 2 horas

##### **Q3.4: engine/memory_engine.py**
 - Tests para: `init_db()`, `save_to_memory()`, `get_from_memory()`
 - Estimación: 1 hora

##### **Q3.5: engine/decision_engine.py**
- Tests para: `run_decision_engine()`, `make_content_decisions()`
- Estimación: 1.5 horas

#### **Tarea Q4: Tests unitarios para utils (4 utils)**

##### **Q4.1: utils/file_utils.py**
- Tests para: `ensure_dir()`, `save_json()`, `load_json()`
- Estimación: 1 hora

##### **Q4.2: utils/json_utils.py**
- Tests para: `validate_json()`, `format_json_output()`
- Estimación: 0.5 horas

##### **Q4.3: utils/logger.py**
- Tests para: `get_logger()`, configuración logging
- Estimación: 0.5 horas

##### **Q4.4: utils/run_context.py**
- Tests para: `init_run()`, `get_run_dir()`
- Estimación: 0.5 horas

#### **Tarea Q5: Tests unitarios para models**

##### **Q5.1: models/request_models.py**
- Tests para: Model classes, validation, serialization
- Estimación: 1 hora

#### **Tarea Q6: Tests para pipeline.py y main.py**

##### **Q6.1: pipeline.py**
- Tests para: `run_reels_pipeline()`, funciones principales
- Estimación: 2 horas

##### **Q6.2: main.py (FastAPI endpoints)**
- Tests para: Endpoints FastAPI usando TestClient
- Estimación: 1.5 horas

#### **Tarea Q7: Documentación para qwen-poc**

##### **Q7.1: Docstrings completos**
- Añadir docstrings a todas las funciones/clases faltantes
- Estimación: 4 horas

##### **Q7.2: README.md específico**
- Crear `qwen-poc/README.md` con:
  - Descripción del módulo
  - Instalación y configuración
  - Ejemplos de uso
  - API documentation
- Estimación: 1.5 horas

##### **Q7.3: Guía de configuración**
- Documentar requirements, API keys, environment variables
- Estimación: 1 hora

### **MÓDULO 2: instagram-upload (PRIORIDAD #2)**

#### **Tarea I1: Verificar tests existentes**

##### **I1.1: Ejecutar todos los tests**
- Ejecutar: `python3 -m pytest instagram-upload/tests/ -v`
- Documentar resultados y failures
- Estimación: 0.5 horas

##### **I1.2: Fixear tests que fallen**
- Debug y fix tests con problemas
- Estimación: 1-2 horas (dependiendo de failures)

#### **Tarea I2: Ampliar tests unitarios**

##### **I2.1: Más tests para browser_service.py**
- Edge cases: timeout, network errors, browser crashes
- Estimación: 1 hora

##### **I2.2: Más tests para cookie_manager.py**
- Cookie expiration, validation, storage issues
- Estimación: 0.5 horas

##### **I2.3: Más tests para login_manager.py**
- Login failures, 2FA scenarios, credential issues
- Estimación: 1 hora

##### **I2.4: Más tests para metadata_handler.py**
- Invalid metadata, Instagram limits, format conversion
- Estimación: 0.5 horas

##### **I2.5: Más tests para publisher.py**
- Upload failures, Instagram API changes, rate limits
- Estimación: 1 hora

##### **I2.6: Más tests para video_uploader.py**
- File issues, network problems, large files
- Estimación: 1 hora

#### **Tarea I3: Tests integration más completos**

##### **I3.1: auth integration tests**
- Complete auth flow testing
- Estimación: 1.5 horas

##### **I3.2: upload integration tests**
- Complete upload flow testing
- Estimación: 1.5 horas

#### **Tarea I4: Documentación para instagram-upload**

##### **I4.1: Docstrings completos**
- Añadir docstrings a funciones faltantes
- Estimación: 2 horas

##### **I4.2: README.md específico**
- Crear `instagram-upload/README.md`
- Estimación: 1 hora

##### **I4.3: Guía de autenticación**
- Documentar cookie management, login process
- Estimación: 1 hora

### **MÓDULO 3: Integration Module (PRIORIDAD #3 - ya bastante completo)**

#### **Tarea M1: Ampliar tests existentes**

##### **M1.1: Más edge cases para metadata adapter**
- Invalid qwen-poc outputs, missing fields
- Estimación: 0.5 horas

##### **M1.2: Tests de performance**
- Medir tiempos de adaptación, validación
- Estimación: 0.5 horas

##### **M1.3: Tests de error scenarios más completos**
- Network failures, file system issues, external API failures
- Estimación: 0.5 horas

#### **Tarea M2: Documentación para integration module**

##### **M2.1: README.md específico**
- Crear `src/integration/README.md`
- Estimación: 0.5 horas

##### **M2.2: Ejemplos más completos**
- Expandir `examples/` con más escenarios
- Estimación: 0.5 horas

### **TAREAS GENERALES DEL PROYECTO**

#### **Tarea G1: Setup CI/CD para tests**

##### **G1.1: Configurar GitHub Actions (o similar)**
- Automatizar ejecución de tests en cada commit
- Estimación: 2 horas

##### **G1.2: Code coverage reporting**
- Configurar pytest-cov para reports automáticos
- Estimación: 1 hora

##### **G1.3: Test badge en README principal**
- Badge mostrando % tests passing
- Estimación: 0.5 horas

#### **Tarea G2: Tests E2E completos**

##### **G2.1: Escenario 1: Mock completo**
- qwen mock → metadata adapter → mock uploader
- Estimación: 0.5 horas (ya parcialmente hecho)

##### **G2.2: Escenario 2: qwen real + mock uploader**
- qwen-poc real → metadata adapter → mock uploader
- Estimación: 1 hora (necesita API keys)

##### **G2.3: Escenario 3: Pipeline completo**
- qwen-poc → metadata adapter → instagram uploader real
- Estimación: 2 horas (depende de decisión B2)

##### **G2.4: Tests de carga/performance**
- Multiple concurrent uploads, large batches
- Estimación: 1.5 horas

#### **Tarea G3: Documentación general del proyecto**

##### **G3.1: README.md principal actualizado**
- Reflejar estado actual con tests y documentación
- Estimación: 1 hora

##### **G3.2: Guía de instalación completa**
- Desde cero hasta ejecución de tests
- Estimación: 1.5 horas

##### **G3.3: Troubleshooting guide**
- Problemas comunes y soluciones
- Estimación: 1 hora

##### **G3.4: Diagramas de arquitectura**
- Diagramas de flujo, componentes, data flow
- Estimación: 2 horas

---

## 📅 **PLAN DE EJECUCIÓN (PROPUESTA)**

### **Fase 1: Setup y primeros tests (Días 1-2)**
1. **Setup testing infrastructure** (Q1) - 2 horas
2. **Ejecutar/verificar tests existentes** (I1) - 1.5 horas
3. **Implementar tests para 3 servicios qwen-poc** (Q2.1-3) - 4 horas
4. **Ampliar tests integration module** (M1) - 1.5 horas

**Total Fase 1:** 9 horas (1-2 días)

### **Fase 2: Tests unitarios core (Días 3-5)**
1. **Implementar tests para 8 servicios qwen-poc** (Q2.4-11) - 12 horas
2. **Implementar tests para engines qwen-poc** (Q3) - 7.5 horas
3. **Ampliar tests instagram-upload** (I2) - 5 horas
4. **CI/CD setup básico** (G1.1) - 2 horas

**Total Fase 2:** 26.5 horas (3-5 días)

### **Fase 3: Tests restantes y documentación (Días 6-8)**
1. **Implementar tests restantes qwen-poc** (Q4-6) - 6.5 horas
2. **Tests E2E** (G2.1-2) - 1.5 horas
3. **Documentación qwen-poc** (Q7) - 6.5 horas
4. **Documentación instagram-upload** (I4) - 4 horas
5. **Documentación integration module** (M2) - 1 hora

**Total Fase 3:** 19.5 horas (3 días)

### **Fase 4: Finalización y polish (Días 9-10)**
1. **Tests E2E completos** (G2.3-4) - 3.5 horas
2. **Documentación general** (G3) - 5.5 horas
3. **CI/CD completo** (G1.2-3) - 1.5 horas
4. **Revisión final y ajustes** - 4 horas

**Total Fase 4:** 14.5 horas (2 días)

### **TOTAL ESTIMADO:**
**~70 horas de trabajo** (10 días con equipo de 4 personas)
**~18 días** si trabajamos solo 4 horas por día en esto

---

## 👥 **ASIGNACIÓN DE TAREAS (PROPUESTA)**

### **Sam Lead Developer:**
- Liderar implementación de tests
- Tests para servicios complejos de qwen-poc
- Tests E2E y integration
- Coordinación general

### **Taylor QA Engineer:**
- Setup testing infrastructure
- Tests unitarios para servicios/engines
- CI/CD configuration
- Code coverage reporting

### **Jordan Documentation Specialist:**
- Todas las tareas de documentación
- Docstrings, READMEs, guías
- Diagramas y examples

### **Casey Code Refactoring Expert:**
- Verificar/fixear tests existentes
- Ampliar tests con edge cases
- Type hints y mejoras de calidad
- Optimización de código para testing

---

## 🚀 **PRIMERAS TAREAS PARA COMENZAR AHORA**

### **Tarea inmediata 1: Setup testing básico**
```bash
# 1. Instalar pytest-cov para coverage reporting
pip install --break-system-packages pytest-cov

# 2. Ejecutar tests existentes con coverage
python3 -m pytest tests/test_integration_pytest.py --cov=src/integration --cov-report=html

# 3. Verificar tests instagram-upload
python3 -m pytest instagram-upload/tests/ -v
```

### **Tarea inmediata 2: Analizar cobertura actual**
- Crear reporte de cobertura actual para cada módulo
- Identificar archivos con 0% cobertura
- Priorizar based on criticality and complexity

### **Tarea inmediata 3: Plan específico para qwen-poc**
- Seleccionar 3 servicios para comenzar (llm_service, search_service, image_service)
- Crear test files específicos para cada servicio
- Implementar primeros tests con mocking

---

## 📋 **CHECKLIST DE PROGRESO**

### **Para cada módulo completado:**
- [ ] 80%+ code coverage (verificado con pytest-cov)
- [ ] Todos los tests pasan
- [ ] Docstrings completos para todas las funciones/clases
- [ ] README.md específico creado
- [ ] Ejemplos de uso incluidos
- [ ] Integration tests funcionando

### **Para proyecto completo:**
- [ ] CI/CD pipeline ejecutando tests automáticamente
- [ ] Code coverage reports disponibles
- [ ] README principal actualizado con badges
- [ ] Guía de instalación completa
- [ ] Tests E2E cubren todos los escenarios principales

---

**Generado por:** Sam Lead Developer  
**Fecha:** 2026-04-09  
**Propósito:** Lista concreta de tareas para llevar proyecto a 100% tests y documentación