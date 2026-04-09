# 🎯 PLAN DE PRUEBAS END-TO-END - PRIORIDAD #1

**Fecha:** 2026-04-08
**Estado:** 🟡 **EN PROGRESO** (B1 y B3 RESUELTOS, B4 pendiente)
**Prioridad:** ABSOLUTA #1 - Antes de cualquier otra cosa

---

## 🚀 **OBJETIVO**

**Probar el pipeline COMPLETO desde selección de tópico hasta upload en Instagram:**

```
[1] qwen-poc/pipeline.py (generación) → 
[2] src/integration/ (adaptación) → 
[3] Instagram upload (real o mock) → 
[4] ✅ PUBLICADO/ERROR (resultado verificable)
```

---

## 📋 **BLOQUEOS CRÍTICOS**

### **✅ B1: Dependencias testing no instaladas - RESUELTO**
- **Impacto:** No podemos crear/ejecutar tests
- **Responsable:** Sam Lead Developer
- **Estado:** ✅ RESUELTO (22:15)
- **Solución aplicada:** `pip install --break-system-packages pytest pytest-asyncio`

### **✅ B3: Dependencias qwen-poc no instaladas - RESUELTO**
- **Impacto:** No podemos ejecutar generación de contenido
- **Responsable:** Sam Lead Developer
- **Estado:** ✅ RESUELTO (22:15)
- **Solución aplicada:** `pip install --break-system-packages fastapi uvicorn dashscope pydantic openai fal-client`

### **🟡 B4: Scripts Python complejos fallando - PENDIENTE**
- **Impacto:** Scripts con imports complejos no ejecutan
- **Responsable:** Casey Code Refactoring Expert
- **Estado:** 🟡 PENDIENTE
- **Solución:** Revisar estructura de imports/paths

---

## 🧪 **ESCENARIOS DE TESTING E2E**

### **Escenario 1: Pipeline completo con mock uploader**
**Objetivo:** Verificar que la integración funciona (sin dependencias externas)
```python
# Flujo:
1. Mock qwen-poc output (sin ejecutar pipeline real)
2. Adaptación a VideoMetadata
3. Upload con MockInstagramUploader
4. Verificar resultado
```

**Estado:** ✅ **COMPLETADO** (10/10 tests pytest pasan, `test_integration_pytest.py`)

### **Escenario 2: Pipeline completo con qwen-poc real**
**Objetivo:** Verificar integración REAL con sistema de generación
```python
# Flujo:
1. Ejecutar qwen-poc/pipeline.py (real)
2. Capturar output real
3. Adaptación a VideoMetadata
4. Upload con MockInstagramUploader
5. Verificar resultado
```

**Estado:** 🟡 **LISTO PARA EJECUTAR** (B3 resuelto, necesita API keys para qwen-poc)

### **Escenario 3: Pipeline completo con uploader real**
**Objetivo:** Verificar sistema COMPLETO end-to-end
```python
# Flujo:
1. Ejecutar qwen-poc/pipeline.py (real)
2. Capturar output real
3. Adaptación a VideoMetadata
4. Upload con InstagramUploader REAL (Graph API o Playwright)
5. Verificar publicación real en Instagram
```

**Estado:** 🟡 **BLOQUEADO POR B3 + B2** (B3 + decisión arquitectónica)

---

## 📊 **PRIORIZACIÓN DE TESTING**

### **PRIORIDAD 1: Escenario 1 (Mock completo)**
- **Valor:** Verifica que nuestro módulo funciona
- **Bloqueos:** Ninguno (ya funciona)
- **Acción:** Expandir tests mock con más casos
- **Responsable:** Sam (hoy)

### **PRIORIDAD 2: Escenario 2 (qwen-poc real + mock uploader)**
- **Valor:** Verifica integración REAL con generación
- **Bloqueos:** B3 (dependencias qwen-poc)
- **Acción:** Taylor debe resolver B3 primero
- **Responsable:** Taylor (URGENTE hoy)

### **PRIORIDAD 3: Escenario 3 (Completo real)**
- **Valor:** Verifica sistema COMPLETO producción
- **Bloqueos:** B3 + B2 + credenciales Instagram
- **Acción:** Resolver B3, decidir B2, obtener credenciales
- **Responsable:** Alex + Taylor + Sam (días siguientes)

---

## 🛠️ **TESTS PARA CREAR HOY**

### **1. Test de adaptación de metadata (`test_metadata_adapter.py`)**
```python
def test_adapt_qwen_to_upload_valid():
    """Test adaptación con output válido de qwen-poc"""
    # Mock qwen output válido
    # Adaptar
    # Verificar VideoMetadata correcto
    
def test_adapt_qwen_to_upload_invalid():
    """Test adaptación con output inválido"""
    # Mock qwen output sin 'final_video_path'
    # Verificar que lanza ValueError
    
def test_validate_metadata_instagram_limits():
    """Test validación contra límites de Instagram"""
    # Metadata con caption > 2200 chars
    # Metadata con >30 hashtags
    # Metadata con file >100MB (simulado)
    # Verificar que validation funciona
```

### **2. Test de PipelineBridge (`test_pipeline_bridge.py`)**
```python
def test_bridge_successful_upload():
    """Test upload exitoso con AlwaysSuccessUploader"""
    # Bridge con AlwaysSuccessUploader
    # Mock qwen output
    # Verificar resultado COMPLETED
    
def test_bridge_failed_upload_with_retry():
    """Test upload fallido con retries"""
    # Bridge con AlwaysFailureUploader
    # Configurar retries
    # Verificar resultado FAILED después de retries
    
def test_bridge_metadata_validation_failure():
    """Test fallo por validación de metadata"""
    # Metadata inválida
    # Verificar resultado FAILED con error apropiado
```

### **3. Test end-to-end mock (`test_e2e_mock.py`)**
```python
def test_full_pipeline_mock_success():
    """Test pipeline completo mock exitoso"""
    # Flujo completo: qwen mock → adaptación → upload mock
    # Verificar todos los pasos funcionan
    
def test_full_pipeline_mock_failure_and_retry():
    """Test pipeline completo con fallos y retries"""
    # Configurar uploader flaky
    # Verificar sistema de retries funciona
```

---

## 📅 **CRONOGRAMA DE TESTING**

### **HOY (2026-04-08):**
1. **Taylor:** Resolver B1 y B3 (dependencias)
2. **Sam:** Crear tests mock (Escenario 1)
3. **Todos:** Verificar tests funcionan

### **MAÑANA (2026-04-09):**
1. **Taylor:** Ejecutar qwen-poc para crear videos de prueba
2. **Sam:** Crear tests con qwen-poc real (Escenario 2)
3. **Alex:** Decidir B2 (uploader real)

### **DÍA 3 (2026-04-10):**
1. **Sam:** Implementar uploader real según decisión B2
2. **Taylor:** Crear tests con uploader real (Escenario 3 parcial)
3. **Jordan:** Documentar proceso de testing

### **DÍA 4-5 (2026-04-11-12):**
1. **Todos:** Ejecutar pruebas end-to-end completas
2. **Taylor:** Reporte de cobertura y calidad
3. **Sam:** Fix bugs encontrados

---

## 🔧 **REQUISITOS PARA TESTING E2E**

### **Hardware/Software:**
- ✅ Python 3.12
- ✅ Dependencias qwen-poc (B3)
- ✅ Dependencias testing (B1)
- ⏳ Credenciales Instagram (para tests reales)
- ⏳ Videos de prueba (generados por qwen-poc)

### **Configuración:**
- ✅ Entorno virtual funcional
- ✅ Acceso a APIs externas (para qwen-poc)
- ✅ Configuración `.env` para qwen-poc
- ⏳ Configuración `.env.instagram` para upload real

### **Conocimiento:**
- ✅ Entender output format de qwen-poc
- ✅ Entender interface InstagramUploader
- ✅ Entender límites y requisitos Instagram
- ✅ Entender sistema de retries y validación

---

## 📝 **CRITERIOS DE ÉXITO**

### **Para Escenario 1 (Mock):**
- ✅ 100% de tests mock pasan
- ✅ Adaptación funciona para múltiples casos
- ✅ Validación detecta todos los errores posibles
- ✅ Sistema de retries funciona en todos los escenarios

### **Para Escenario 2 (qwen-poc real + mock):**
- ✅ qwen-poc puede ejecutarse y generar contenido
- ✅ Output real puede ser adaptado correctamente
- ✅ Integración no tiene bugs
- ✅ Performance aceptable (<30s total)

### **Para Escenario 3 (Completo real):**
- ✅ Video publicado REAL en Instagram (sandbox/test account)
- ✅ Metadata transferida correctamente (caption, hashtags)
- ✅ Sistema maneja errores reales (rate limits, auth issues)
- ✅ Logging y métricas funcionan en producción

---

## 🚨 **RIESGOS Y MITIGACIÓN**

### **Riesgo 1: qwen-poc no funciona**
- **Mitigación:** Tests mock primero, Taylor focus en B3

### **Riesgo 2: Instagram API/UI cambios**
- **Mitigación:** Tests con mock, uploader abstracto flexible

### **Riesgo 3: Credenciales no disponibles**
- **Mitigación:** Tests con mock, sandbox account para pruebas reales

### **Riesgo 4: Performance issues**
- **Mitigación:** Métricas en tests, optimización iterativa

---

## 📞 **RESPONSABILIDADES**

### **Taylor QA Engineer (PRIORIDAD):**
- ✅ Resolver B1 y B3 (HOY URGENTE)
- ✅ Configurar entorno testing
- ✅ Crear videos de prueba con qwen-poc
- ✅ Ejecutar y reportar tests

### **Sam Lead Developer:**
- ✅ Crear tests mock mientras Taylor resolve bloqueos
- ✅ Implementar uploader real cuando B2 decidido
- ✅ Fix bugs encontrados en testing

### **Alex Technical Architect:**
- ✅ Decidir B2 rápido para avanzar a tests reales
- ✅ Validar arquitectura durante testing
- ✅ Aprobar solución para bloqueos

### **Jordan Documentation Specialist:**
- ✅ Documentar proceso de testing
- ✅ Documentar bugs encontrados y fixes
- ✅ Crear guía de troubleshooting

### **Casey Code Refactoring Expert:**
- ✅ Revisar código de tests para calidad
- ✅ Sugerir mejoras basadas en testing
- ✅ Asegurar principios SOLID en tests

---

## 🎯 **MEDICIÓN DE PROGRESO**

### **Métrica 1: % tests implementados**
- **Objetivo:** 100% tests mock hoy
- **Actual:** 0%
- **Check:** Cada 2 horas

### **Métrica 2: % bloqueos resueltos**
- **Objetivo:** B1+B3 resueltos hoy
- **Actual:** 0%
- **Check:** Cada hora

### **Métrica 3: % escenarios testing funcionando**
- **Objetivo:** Escenario 1 hoy, Escenario 2 mañana
- **Actual:** Escenario 1 parcial (demo)
- **Check:** Daily standup

---

**Última actualización:** 2026-04-08 21:42  
**Próxima revisión:** 21:45 (3 minutos)  
**Responsable:** Taylor QA Engineer (bloqueos) + Sam (tests)