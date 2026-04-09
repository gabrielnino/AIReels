# REGLA ESTRICTA: No Commit Sin Tests Unitarios

**Estado:** ACTIVO  
**Severidad:** BLOQUEANTE  
**Vigencia:** Inmediata y permanente  
**Aplicable a:** Todo el equipo de desarrollo

## 1. Regla Fundamental

### ❌ PROHIBIDO ABSOLUTAMENTE
- **Commits** sin tests unitarios correspondientes
- **Merge de PRs** con cobertura de tests < 80% para código nuevo
- **Deploys a producción** con tests fallando
- **Modificaciones a código existente** sin actualizar tests afectados

### ✅ REQUERIDO OBLIGATORIAMENTE
- **Tests unitarios** para toda funcionalidad nueva
- **Cobertura mínima** del 80% para código nuevo
- **Tests de regresión** para modificaciones a código existente
- **Aprobación de QA Automation** antes de cualquier merge

## 2. Criterios de Validación

### 2.1 Para Código Nuevo
| Criterio | Mínimo Requerido | Verificación | Bloqueo si falla |
|----------|------------------|--------------|------------------|
| Cobertura de tests | 80% | CI/CD pipeline | ✅ SI |
| Tests unitarios | 1 test por función pública | Code review | ✅ SI |
| Tests de integración | Para componentes que interactúan | QA Automation | ✅ SI |
| Edge cases | Tests para casos límite | QA review | ⚠️ WARNING |

### 2.2 Para Modificaciones a Código Existente
| Criterio | Mínimo Requerido | Verificación | Bloqueo si falla |
|----------|------------------|--------------|------------------|
| Tests existentes | Deben seguir pasando | CI/CD pipeline | ✅ SI |
| Cobertura | No disminuir cobertura existente | Coverage check | ✅ SI |
| Tests nuevos | Para nueva lógica introducida | Code review | ✅ SI |
| Refactor tests | Actualizar tests obsoletos | Refactor Developer | ✅ SI |

## 3. Proceso de Bloqueo

### 3.1 Git Hooks Preventivos
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Verificar tests unitarios para cambios
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM "*.py")

for file in $CHANGED_FILES; do
    # Verificar si hay tests correspondientes
    TEST_FILE="tests/test_$(basename $file)"
    if [ ! -f "$TEST_FILE" ] && [[ $file != test_* ]]; then
        echo "❌ ERROR: No hay tests para $file"
        echo "   Crear: $TEST_FILE"
        exit 1
    fi
done

# Ejecutar tests rápidos
pytest --tb=short -q
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Tests fallaron"
    exit 1
fi

echo "✅ Tests pasaron, commit permitido"
exit 0
```

### 3.2 CI/CD Pipeline
```yaml
# .github/workflows/block-without-tests.yml
name: Block Without Tests
on: [push, pull_request]

jobs:
  validate-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
      
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-test.txt
      
      - name: Check test coverage for new code
        run: |
          # Analizar cobertura solo para código nuevo/modificado
          NEW_FILES=$(git diff --name-only main...HEAD -- "*.py" | grep -v test_)
          if [ -n "$NEW_FILES" ]; then
            pytest --cov=. --cov-report=xml $NEW_FILES
            coverage report --fail-under=80
          else
            echo "No hay archivos Python nuevos"
          fi
      
      - name: Block if coverage < 80%
        if: failure()
        run: |
          echo "❌ BLOQUEO: Cobertura de tests insuficiente (< 80%)"
          echo "🚫 Este PR no puede ser mergeado"
          exit 1
```

## 4. Roles y Responsabilidades

### 4.1 Main Developer
- **Responsabilidad:** Escribir tests unitarios junto con el código
- **Checklist pre-commit:**
  - [ ] Tests para cada función/método nuevo
  - [ ] Tests para edge cases y casos de error
  - [ ] Mocks para dependencias externas
  - [ ] Cobertura > 80% localmente verificada

### 4.2 QA Automation
- **Responsabilidad:** Validar calidad de tests y cobertura
- **Poderes:**
  - ✅ **Rechazar** PRs sin tests adecuados
  - ✅ **Requerir** tests adicionales
  - ✅ **Bloquear** merge si cobertura < 80%
  - ✅ **Aprobar** solo cuando criterios se cumplen

### 4.3 Refactor Developer
- **Responsabilidad:** Mantener tests actualizados durante refactorización
- **Reglas:**
  - Mantener o mejorar cobertura existente
  - Refactorizar tests junto con código de producción
  - Asegurar tests siguen siendo relevantes y efectivos

### 4.4 Arquitecto
- **Responsabilidad:** Hacer cumplir la regla a nivel arquitectónico
- **Acciones:**
  - Revisar que diseño facilite testing
  - Aprobar solo arquitecturas testables
  - Requerir patrones que permitan mocking

## 5. Excepciones (MUY LIMITADAS)

### 5.1 Tipos de Excepciones Permitidas
1. **Configuración/Boilerplate:** Archivos puramente de configuración
2. **Documentación:** Comentarios, docstrings, archivos .md
3. **Assets estáticos:** Imágenes, CSS, templates sin lógica

### 5.2 Proceso de Excepción
1. **Solicitud:** Crear issue con justificación
2. **Aprobación:** Requiere 2 aprobaciones (QA + Arquitecto)
3. **Registro:** Se documenta en `EXCEPTIONS_LOG.md`
4. **Revisión:** Re-evaluación cada 30 días

## 6. Consecuencias por Incumplimiento

### 6.1 Primera Ocurrencia
- **Acción:** Revertir commit
- **Notificación:** Warning al desarrollador
- **Requerimiento:** Training en testing básico
- **Tiempo:** 24 horas para corregir

### 6.2 Segunda Ocurrencia
- **Acción:** Bloqueo de commits por 48 horas
- **Notificación:** Manager/Arquitecto notificado
- **Requerimiento:** Pair programming con QA Automation
- **Revisión:** Todos commits previos del desarrollador

### 6.3 Tercera Ocurrencia+
- **Acción:** Bloqueo permanente hasta resolución
- **Notificación:** Escalación a leadership
- **Requerimiento:** Curso formal de testing
- **Consecuencia:** Impacto en evaluación de desempeño

## 7. Herramientas de Validación

### 7.1 Local (Pre-commit)
```bash
# Script de validación local
./scripts/validate_tests.sh

# Verificar cobertura
pytest --cov=. --cov-report=term-missing

# Verificar tests rotos
pytest --tb=short -v
```

### 7.2 CI/CD (Automático)
```yaml
# Workflow steps
- name: Test Coverage Check
  uses: codecov/codecov-action@v3
  with:
    fail_ci_if_error: true
    flags: unittests
  
- name: Test Execution
  run: |
    pytest --junitxml=test-results.xml
    test $? -eq 0 || exit 1
```

### 7.3 Monitoreo Continuo
```python
# dashboard_test_coverage.py
import requests
import json

def get_coverage_dashboard():
    """Dashboard de cobertura de tests."""
    return {
        "current_coverage": get_current_coverage(),
        "trend": get_coverage_trend(),
        "violations": get_recent_violations(),
        "blocked_prs": get_blocked_prs_count()
    }
```

## 8. Métricas y Reportes

### 8.1 Métricas Diarias
- **Test Coverage:** % cobertura total
- **New Code Coverage:** % cobertura código nuevo
- **Test Pass Rate:** % tests pasando
- **Blocked Commits:** # commits bloqueados
- **Violations:** # violaciones a la regla

### 8.2 Reporte Semanal
```markdown
# Reporte Semanal: No Commit Without Tests
**Semana:** 2026-04-08 al 2026-04-14

## Resumen
- Cobertura total: 85% ▲ 2%
- Código nuevo cubierto: 92% ▲ 5%
- Commits bloqueados: 3 ▼ 8
- PRs rechazados: 1 ▼ 4

## Incidencias
1. PR #45 rechazado - cobertura 65% (Main Developer: Juan)
2. Commit revertido - sin tests (Main Developer: María)

## Tendencia
✅ Mejora continua en adopción de tests
⚠️ Necesidad de training para 2 desarrolladores
```

## 9. Onboarding para Nuevos Desarrolladores

### 9.1 Training Obligatorio
1. **Testing 101:** Fundamentos de pruebas unitarias (2 horas)
2. **Pytest Workshop:** Herramientas y mejores prácticas (3 horas)
3. **Mocking Dependencies:** Aislamiento de tests (2 horas)
4. **CI/CD Testing:** Integración con pipeline (1 hora)

### 9.2 Período de Prueba
- **Días 1-7:** Commits solo con supervisión de QA
- **Días 8-30:** Revisión 100% de tests por QA Automation
- **Día 31+:** Autonomía con monitoreo periódico

## 10. Recursos y Referencias

### 10.1 Documentación
- [Guía de Testing](CODING_STANDARDS.md#4-testing)
- [Ejemplos de Tests](examples/tests/)
- [Plantillas de Tests](templates/test_templates.py)

### 10.2 Herramientas
- `pytest`: Framework de testing
- `coverage.py`: Medición de cobertura
- `pytest-cov`: Integración coverage + pytest
- `pytest-mock`: Mocking integrado

### 10.3 Soporte
- **QA Automation:** Ayuda con estrategia de testing
- **Refactor Developer:** Ayuda con refactorización de tests
- **Arquitecto:** Consultas sobre testabilidad de arquitectura

---

**Esta regla es innegociable y se aplica sin excepciones.**  
**La calidad del código es responsabilidad de todo el equipo.**  
**Última actualización:** 2026-04-08  
**Aprobado por:** Arquitecto, QA Automation, Main Developer