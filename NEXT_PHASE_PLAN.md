# 📋 PLAN PARA LA SIGUIENTE FASE - POST ATAQUE COORDINADO

**Fecha:** 2026-04-09  
**Basado en:** Resultados del ataque coordinado (122/138 tests pasando)  
**Objetivo:** Reducir tests fallidos de 16 a <8 en próxima sesión

---

## 📊 ESTADO ACTUAL POST-ATAQUE

### **Métricas Globales:**
- **Total tests:** 138
- **Tests pasando:** 122 (88.4%)
- **Tests fallidos:** 16 (11.6%)
- **Mejora desde inicio:** -5 tests fallidos (21 → 16)

### **Distribución de Tests Fallidos:**
| Módulo | Tests Fallidos | % del Total Fallidos |
|--------|---------------|----------------------|
| **publisher.py** | 6 | 37.5% |
| **login_manager.py** | 4 | 25.0% |
| **browser_service.py** | 2 | 12.5% |
| **cookie_manager.py** | 2 | 12.5% |
| **metadata_handler.py** | 1 | 6.25% |
| **auth_integration.py** | 1 | 6.25% |

---

## 🎯 PRIORIZACIÓN POR IMPACTO

### **🟢 PRIORIDAD 1: publisher.py (6 tests)**
**Impacto:** Módulo core para publicación en Instagram  
**Issues identificados:**
1. Dry run logic inconsistent
2. Mock assertion failures
3. BrowserService requirement checks

**Acciones recomendadas:**
1. Revisar lógica de dry run en `Publisher` class
2. Ajustar mocks para assertions correctos
3. Verificar flujo completo de publicación

### **🟡 PRIORIDAD 2: login_manager.py (4 tests)**
**Impacto:** Autenticación crítica para todo el sistema  
**Issues identificados:**
1. `async_playwright` import incorrecto
2. Environment variables mocking
3. Mock context manager protocol

**Acciones recomendadas:**
1. Corregir imports de async_playwright
2. Usar `unittest.mock.patch.dict` para env vars
3. Mock `open()` function correctamente

### **🔵 PRIORIDAD 3: browser_service.py (2 tests)**
**Impacto:** Componente fundamental para automation  
**Issues identificados:**
1. AsyncMock behavior con `.is_visible()`
2. AsyncMock behavior con `.text_content()`

**Acciones recomendadas:**
1. Ajustar AsyncMock para devolver valores en lugar de mocks
2. Verificar chain mocking de `.first`

---

## 👥 ASIGNACIÓN PARA SIGUIENTE SESIÓN

### **Sesión de 1.5 horas (mañana 09:00-10:30)**

#### **Grupo A: publisher.py fixes (Sam + Casey)**
- **Objetivo:** Resolver 4/6 tests fallidos
- **Focus:** Dry run logic y assertion fixes
- **Tiempo:** 45 minutos

#### **Grupo B: login_manager.py fixes (Taylor + Jordan)**
- **Objetivo:** Resolver 3/4 tests fallidos  
- **Focus:** Imports y env vars mocking
- **Tiempo:** 45 minutos

#### **Grupo Combinado: browser_service.py (todos últimos 30 min)**
- **Objetivo:** Resolver 2/2 tests fallidos
- **Focus:** AsyncMock behavior final fixes
- **Tiempo:** 30 minutos

---

## 🛠️ HERRAMIENTAS Y TÁCTICAS

### **Para publisher.py:**
```python
# Fix dry run logic
def test_method():
    publisher._dry_run = True  # Set before test
    # Test logic
```

### **Para login_manager.py:**
```python
# Fix async_playwright import
with patch('playwright.async_api.async_playwright') as mock_playwright:
    # Test logic

# Fix env vars
with patch.dict(os.environ, {'INSTAGRAM_USERNAME': 'test'}):
    # Test logic
```

### **Para browser_service.py:**
```python
# Fix AsyncMock behavior
mock_element.is_visible = AsyncMock(return_value=True)
# Asegurar que await mock_element.is_visible() devuelve True
```

---

## 📈 OBJETIVOS CUANTITATIVOS

### **Para próxima sesión (1.5 horas):**
- **Total tests fallidos objetivo:** <8 (de 16 actual)
- **Reducción necesaria:** 8+ tests
- **Distribución por módulo:**
  - publisher.py: 6 → 2 (4 resueltos)
  - login_manager.py: 4 → 1 (3 resueltos)  
  - browser_service.py: 2 → 0 (2 resueltos)
  - Otros: 4 → 4 (mantener)

### **Métrica de éxito:** 130/138 tests pasando (94%)

---

## 📋 CHECKLIST DE PREPARACIÓN

### **Antes de comenzar:**
- [ ] Verificar que `run_tests_fixed.sh` funciona
- [ ] `.env.test` presente y cargado
- [ ] `conftest.py` configurado en ambos niveles
- [ ] playwright instalado en sistema

### **Durante sesión:**
- [ ] Actualizar `TEAM_TASK_UPDATES.md` cada 15 minutos
- [ ] Ejecutar tests específicos (no suite completa)
- [ ] Documentar root causes encontradas
- [ ] Crear fixes reutilizables

### **Al finalizar:**
- [ ] Ejecutar suite completa
- [ ] Actualizar `TEST_COVERAGE_REPORT.md`
- [ ] Documentar lecciones aprendidas
- [ ] Planificar siguiente sesión

---

## 🚨 PLAN DE CONTINGENCIA

### **Si no alcanzamos objetivo a los 60 minutos:**
1. **Priorizar tests de integration module** (ya 100% pasando)
2. **Marcar tests más complejos como `@pytest.mark.skip`** con razón
3. **Focus en cobertura** más que 100% pass rate

### **Si hay bloqueos técnicos:**
1. Documentar issue específico en `BLOCKERS_AND_SOLUTIONS.md`
2. Considerar reescribir test problemático
3. Buscar approach alternativo (mocking diferente)

---

## 📞 COMUNICACIÓN DURANTE SESIÓN

### **Canal:** `#next-phase-fixes`
### **Checkpoints:**
- **09:15:** Status inicial (setup completado)
- **09:45:** Progreso mitad de sesión
- **10:15:** Últimos 15 minutos
- **10:30:** Resultados finales

### **Formato de update:**
```
## [HH:MM] - [GRUPO] - [MÓDULO]
**Tests resueltos:** X/Y
**Issues específicos:** [descripción]
**Próximo:** [acción]
```

---

## 🎯 METAS DE LARGO PLAZO

### **1 semana:** 95%+ tests pasando (<7 fallidos)
### **2 semanas:** CI/CD pipeline funcional
### **1 mes:** 100% tests pasando + coverage >80%

### **Próximos módulos a atacar:**
1. qwen-poc tests unitarios
2. Integration module edge cases
3. Performance/stress tests

---

## ✅ CRITERIOS DE ÉXITO PARA PRÓXIMA SESIÓN

1. **Tests fallidos <8** (de 16 actual)
2. **Sistema de testing sigue funcional**
3. **Documentación actualizada**
4. **Plan claro para siguiente fase**

---

**🚀 EL EQUIPO ESTÁ PREPARADO PARA CONTINUAR EL TRABAJO**

**⏰ Próxima sesión:** 2026-04-10 09:00  
**🎯 Objetivo:** Reducir tests fallidos a <8

---
*Generado basado en resultados del ataque coordinado - 2026-04-09 20:57*