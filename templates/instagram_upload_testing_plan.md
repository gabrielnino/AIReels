# Plan de Testing: Instagram Upload Service

**Responsable:** QA Automation
**Funcionalidad:** Auto-upload a Instagram Reels
**Cobertura Objetivo:** > 85% código nuevo
**Fecha Inicio:** [Fecha después de aprobación]
**Fecha Fin:** [Fecha + 5 días]

## 1. Estrategia de Testing

### 1.1 Niveles de Testing
1. **Unit Tests:** Funciones individuales (Mock de Instagram API)
2. **Integration Tests:** Componentes trabajando juntos (Sandbox API)
3. **E2E Tests:** Flujo completo (Ambiente staging)
4. **Performance Tests:** Carga y stress testing
5. **Security Tests:** Validación de autenticación y tokens

### 1.2 Criterios de Éxito
- [ ] Todos los tests pasan en CI/CD
- [ ] Cobertura > 85% para código nuevo
- [ ] Cobertura > 70% para modificaciones a código existente
- [ ] No decrease en cobertura general del proyecto
- [ ] Performance dentro de límites especificados
- [ ] Zero regressions en funcionalidad existente

## 2. Test Cases por Componente

### 2.1 InstagramAuthService
| ID | Descripción | Tipo | Pre-condiciones | Pasos | Resultado Esperado | Prioridad |
|----|-------------|------|-----------------|-------|-------------------|-----------|
| AUTH-001 | Login exitoso | Unit | Credenciales válidas | Llamar authenticate() | Token de acceso válido | Alta |
| AUTH-002 | Credenciales inválidas | Unit | Credenciales incorrectas | Llamar authenticate() | AuthenticationError | Alta |
| AUTH-003 | Token refresh | Unit | Token expirado | Llamar refresh_token() | Nuevo token válido | Alta |
| AUTH-004 | Múltiples cuentas | Integration | 2+ cuentas configuradas | Autenticar ambas | Tokens independientes | Media |
| AUTH-005 | Rate limiting | Integration | Límites excedidos | Intentos consecutivos | Exponential backoff aplicado | Media |

### 2.2 VideoUploadService
| ID | Descripción | Tipo | Pre-condiciones | Pasos | Resultado Esperado | Prioridad |
|----|-------------|------|-----------------|-------|-------------------|-----------|
| UPL-001 | Upload exitoso | Integration | Video válido < 90s | Subir video | Media ID retornado | Alta |
| UPL-002 | Video muy grande | Unit | Video > 100MB | Validar tamaño | ValidationError | Alta |
| UPL-003 | Formato no soportado | Unit | Formato .avi | Validar formato | ValidationError | Alta |
| UPL-004 | Timeout de red | Integration | Simular timeout | Subir con timeout | Retry después de timeout | Alta |
| UPL-005 | Upload parcial | Integration | Conexión interrumpida | Interrumpir upload | Reintentar desde punto de interrupción | Media |

### 2.3 MetadataManager
| ID | Descripción | Tipo | Pre-condiciones | Pasos | Resultado Esperado | Prioridad |
|----|-------------|------|-----------------|-------|-------------------|-----------|
| META-001 | Caption válido | Unit | Texto < 2200 chars | Aplicar caption | Caption aceptado | Alta |
| META-002 | Caption muy largo | Unit | Texto > 2200 chars | Validar caption | ValidationError | Alta |
| META-003 | Hashtags procesados | Unit | 30 hashtags | Procesar hashtags | Hashtags formateados correctamente | Media |
| META-004 | Too many hashtags | Unit | 31+ hashtags | Validar hashtags | ValidationError | Media |
| META-005 | Location válida | Integration | Coordenadas válidas | Aplicar location | Location ID aceptado | Baja |

### 2.4 SchedulerService
| ID | Descripción | Tipo | Pre-condiciones | Pasos | Resultado Esperado | Prioridad |
|----|-------------|------|-----------------|-------|-------------------|-----------|
| SCH-001 | Programación futura | Integration | Fecha futura válida | Programar publicación | Tarea creada en queue | Alta |
| SCH-002 | Fecha pasada | Unit | Fecha en pasado | Validar fecha | ValidationError | Alta |
| SCH-003 | Ejecución programada | E2E | Tarea programada | Esperar tiempo | Upload ejecutado automáticamente | Alta |
| SCH-004 | Cancelación | Integration | Tarea programada | Cancelar tarea | Tarea removida de queue | Media |
| SCH-005 | Múltiples programaciones | Performance | 100+ tareas | Programar masivamente | Todas procesadas correctamente | Media |

## 3. Test Data

### 3.1 Videos de Prueba
| Nombre | Duración | Tamaño | Formato | Propósito |
|--------|----------|--------|---------|-----------|
| test_short.mp4 | 15s | 5MB | MP4 | Tests básicos |
| test_medium.mp4 | 60s | 25MB | MP4 | Tests de performance |
| test_limit.mp4 | 90s | 40MB | MP4 | Tests de límites |
| test_invalid.avi | 30s | 15MB | AVI | Tests de formato |
| test_large.mp4 | 120s | 150MB | MP4 | Tests de validación |

### 3.2 Credenciales de Prueba
- **Sandbox Instagram Account:** [Cuenta de desarrollo]
- **Test User Tokens:** [Tokens de prueba]
- **Invalid Tokens:** [Tokens expirados/revocados]
- **Rate Limited Tokens:** [Tokens con límites excedidos]

## 4. Entornos de Testing

### 4.1 Local Development
- **Propósito:** Desarrollo y tests unitarios
- **Instagram API:** Mock completo
- **Base de Datos:** SQLite en memoria
- **Queue:** Celery con broker en memoria
- **Storage:** Sistema de archivos local

### 4.2 CI/CD Pipeline
- **Propósito:** Tests automatizados en PRs
- **Instagram API:** Sandbox con credenciales de test
- **Base de Datos:** PostgreSQL temporal
- **Queue:** Redis en contenedor Docker
- **Storage:** Directorio temporal

### 4.3 Staging Environment
- **Propósito:** Tests de integración y E2E
- **Instagram API:** Sandbox con credenciales reales
- **Base de Datos:** PostgreSQL dedicado
- **Queue:** Redis cluster
- **Storage:** S3 bucket de staging

## 5. Automatización

### 5.1 Test Suites
```python
# Estructura de tests
tests/
├── unit/
│   ├── test_instagram_auth.py
│   ├── test_video_upload.py
│   ├── test_metadata_manager.py
│   └── test_scheduler.py
├── integration/
│   ├── test_auth_integration.py
│   ├── test_upload_integration.py
│   └── test_full_flow.py
├── e2e/
│   └── test_instagram_upload_e2e.py
└── performance/
    └── test_upload_performance.py
```

### 5.2 CI/CD Configuration
```yaml
# .github/workflows/instagram-tests.yml
name: Instagram Upload Tests
on: [push, pull_request]

jobs:
  test-instagram:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpassword
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-test.txt
      
      - name: Run unit tests
        run: pytest tests/unit/ --cov=instagram_upload --cov-report=xml
      
      - name: Run integration tests
        run: |
          export INSTAGRAM_API_KEY=${{ secrets.INSTAGRAM_TEST_KEY }}
          pytest tests/integration/ --cov=instagram_upload --cov-append
      
      - name: Check coverage
        run: |
          coverage report --fail-under=85
          coverage html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 6. Métricas de Calidad

### 6.1 Métricas a Medir
- **Cobertura de Código:** > 85% para código nuevo
- **Test Pass Rate:** 100% en CI/CD
- **Test Execution Time:** < 10 minutos
- **False Positive Rate:** < 5%
- **Defect Detection Rate:** > 90%

### 6.2 Monitoreo de Tests
```python
# test_metrics.py
import pytest
from datetime import datetime

class TestMetrics:
    def test_coverage(self):
        """Verifica cobertura mínima."""
        coverage = get_code_coverage()
        assert coverage >= 85, f"Cobertura insuficiente: {coverage}%"
    
    def test_performance(self):
        """Verifica tiempo de ejecución de tests."""
        start_time = datetime.now()
        # Ejecutar suite de tests
        execution_time = (datetime.now() - start_time).total_seconds()
        assert execution_time < 600, f"Tests muy lentos: {execution_time}s"
    
    def test_flaky_tests(self):
        """Identifica tests flaky."""
        flaky_tests = detect_flaky_tests()
        assert len(flaky_tests) == 0, f"Tests flaky encontrados: {flaky_tests}"
```

## 7. Checklist de Aprobación para Merge

### 7.1 Requisitos Obligatorios
- [ ] Todos los tests unitarios pasan (100%)
- [ ] Cobertura > 85% para código nuevo
- [ ] Tests de integración pasan con sandbox API
- [ ] No regressions en tests existentes
- [ ] Performance dentro de límites aceptables
- [ ] Linting y type checking pasan

### 7.2 Validación Manual (Opcional)
- [ ] Review de casos de prueba por Main Developer
- [ ] Validación de test data por Documentator
- [ ] Aprobación de estrategia por Arquitecto
- [ ] Verificación de métricas por QA Lead

## 8. Plan de Mitigación de Riesgos

### 8.1 Riesgo: Cambios en Instagram API
- **Mitigación:** Webhooks para notificaciones de cambios
- **Monitorización:** Tests diarios de conectividad
- **Contingencia:** Mock completo para desarrollo

### 8.2 Riesgo: Tests Flaky
- **Mitigación:** Re-ejecución automática de tests fallidos
- **Monitorización:** Dashboard de estabilidad de tests
- **Contingencia:** Exclusión temporal con ticket de seguimiento

### 8.3 Riesgo: Performance en CI/CD
- **Mitigación:** Parallel test execution
- **Monitorización:** Métricas de tiempo de ejecución
- **Contingencia:** División de test suites

## 9. Entregables

### 9.1 Documentación Técnica
- [ ] Especificación de test cases
- [ ] Configuración de entornos de testing
- [ ] Guía de ejecución de tests
- [ ] Reporte de cobertura de código

### 9.2 Código
- [ ] Test suites completas
- [ ] Fixtures y test data
- [ ] Mocks de Instagram API
- [ ] Scripts de configuración

### 9.3 Reportes
- [ ] Reporte de cobertura (HTML/XML)
- [ ] Reporte de ejecución de tests
- [ ] Análisis de performance
- [ ] Identificación de gaps de testing

## 10. Timeline

| Fase | Duración | Entregables | Criterio de Éxito |
|------|----------|-------------|-------------------|
| **Fase 1:** Diseño | 1 día | Test strategy, casos de prueba | Aprobación por Arquitecto |
| **Fase 2:** Implementación Unit | 2 días | Tests unitarios, mocks | Cobertura > 85% |
| **Fase 3:** Implementación Integration | 1.5 días | Tests de integración | Conexión con sandbox API |
| **Fase 4:** Implementación E2E | 1 día | Tests end-to-end | Flujo completo funcionando |
| **Fase 5:** Performance Testing | 0.5 días | Tests de carga | Performance dentro de límites |
| **Fase 6:** Documentación | 1 día | Reportes, guías | Documentación completa |

**Total:** 7 días

---

**Aprobado por:** QA Automation  
**Revisado por:** Main Developer  
**Fecha:** 2026-04-08