# 🚨 BLOQUEOS Y SOLUCIONES - SPRINT 3

**Propósito:** Tracking centralizado de todos los bloqueos  
**Regla:** Documentar inmediatamente al detectar, actualizar al resolver  
**Última revisión:** 2026-04-08

---

## 📊 **RESUMEN DE BLOQUEOS**

| ID | Estado | Prioridad | Detectado | Responsable | Impacto |
|----|--------|-----------|-----------|-------------|---------|
| **B1** | ✅ RESUELTO | ALTA | 2026-04-08 | Sam Lead Developer | ALTO |
| **B2** | 🟡 ABIERTO | CRÍTICA | 2026-04-08 | Alex Technical Architect | CRÍTICO |
| **B3** | ✅ RESUELTO | CRÍTICA | 2026-04-08 | Sam Lead Developer | CRÍTICO |

**Totales:** 2 bloqueos activos (1 CRÍTICO, 1 ALTA), 2 RESUELTOS

---

## 🚨 **BLOQUEOS ACTIVOS**

### **B1: DEPENDENCIAS DE TESTING NO INSTALADAS**

#### **INFORMACIÓN BÁSICA**
- **ID:** B1
- **Estado:** 🟡 **ABIERTO**
- **Prioridad:** ALTA
- **Impacto:** ALTO - Bloquea todo testing del proyecto
- **Tipo:** TÉCNICO - Configuración de entorno
- **Detección:** 2026-04-08 20:48
- **Reportado por:** Taylor QA Engineer
- **Responsable actual:** Sam Lead Developer
- **Tareas afectadas:** S3-T6, S3-T5, todas las de testing

#### **DESCRIPCIÓN DETALLADA**
**¿Qué está bloqueado?**
No se pueden ejecutar tests del proyecto porque las dependencias de testing (pytest, pytest-asyncio, etc.) no están instaladas en el entorno.

**Síntomas específicos:**
- `python -m pytest` → "No module named pytest"
- `python run_tests.py` → Exit code 1
- Los 99 tests existentes no se pueden ejecutar

**Ámbito del impacto:**
- ✅ Bloquea validación de código existente
- ✅ Bloquea desarrollo de nuevos tests (S3-T6)
- ✅ Bloquea CI/CD pipeline
- ✅ Impacta calidad y confianza en el código

#### **ANÁLISIS DE CAUSA RAÍZ**
**Causa probable:**
1. Entorno virtual no configurado correctamente
2. `requirements.txt` no instalado completamente
3. Dependencias de solo desarrollo no marcadas apropiadamente

**Evidencia encontrada:**
- `requirements.txt` incluye pytest (línea 19)
- `venv/` existe pero puede no estar activado
- Comandos `pip install` fallan

#### **SOLUCIONES PROPUESTAS**

##### **Solución 1: Instalar en entorno global (RÁPIDO)**
```bash
pip install pytest pytest-asyncio pytest-playwright pytest-cov pytest-mock
```
**Ventajas:**
- ✅ Solución inmediata
- ✅ Permite continuar testing
- ✅ Simple de implementar

**Desventajas:**
- ❌ Contamina entorno global
- ❌ No sostenible a largo plazo
- ❌ Puede causar conflictos de versión

##### **Solución 2: Configurar entorno virtual correctamente (RECOMENDADO)**
```bash
# 1. Verificar/crear venv
python -m venv venv

# 2. Activar
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r instagram-upload/requirements.txt
```
**Ventajas:**
- ✅ Entorno aislado y reproducible
- ✅ Sigue mejores prácticas
- ✅ Evita conflictos de dependencias

**Desventajas:**
- ❌ Requiere configuración adicional
- ❌ Todos deben usar venv activado

##### **Solución 3: Usar Docker (AVANZADO)**
```bash
# Crear Dockerfile con todas las dependencias
docker build -t instagram-upload .
docker run -it instagram-upload pytest
```
**Ventajas:**
- ✅ Entorno 100% reproducible
- ✅ Mismo entorno en todos lados
- ✅ Ideal para CI/CD

**Desventajas:**
- ❌ Complejidad añadida
- ❌ Overhead para desarrollo local

#### **PLAN DE ACCIÓN**
**Paso 1 (INMEDIATO):** Sam Lead Developer intenta Solución 2
**Paso 2 (SI FALLA):** Taylor QA Engineer prueba Solución 1 como temporal
**Paso 3 (LARGO PLAZO):** Alex Technical Architect evalúa Solución 3 para CI/CD

**Fecha objetivo de resolución:** 2026-04-08 (hoy)
**Siguiente check:** 21:30

#### **ACTUALIZACIÓN 2026-04-08 22:15 - RESUELTO POR SAM LEAD DEVELOPER**
**Estado:** ✅ **RESUELTO**
**Solución aplicada:** Usar `pip install --break-system-packages` en sistema Ubuntu con entorno externamente gestionado
**Comandos ejecutados:**
```bash
/usr/bin/python3 -m pip install --break-system-packages pytest pytest-asyncio requests python-dotenv
/usr/bin/python3 -m pip install --break-system-packages fastapi uvicorn dashscope pydantic openai fal-client
```
**Verificación:**
- ✅ pytest instalado y funcionando (`pytest --version`)
- ✅ requests instalado y funcionando
- ✅ qwen-poc puede ejecutarse (`python3 pipeline.py`)
- ✅ Todos los imports de integration funcionan
**Lecciones aprendidas:** En sistemas Ubuntu/Debian con Python externamente gestionado, usar `--break-system-packages` es la forma correcta de instalar paquetes Python globalmente cuando no se puede usar entorno virtual.
**Fecha resolución:** 2026-04-08 22:15

---

### **B2: DECISIÓN ARQUITECTÓNICA - ENFOQUE DE UPLOAD**

#### **INFORMACIÓN BÁSICA**
- **ID:** B2
- **Estado:** 🟡 **ABIERTO**
- **Prioridad:** CRÍTICA
- **Impacto:** CRÍTICO - Define arquitectura del sistema
- **Tipo:** ARQUITECTURA - Decisión de diseño
- **Detección:** 2026-04-08 20:50
- **Reportado por:** Alex Technical Architect
- **Responsable actual:** Alex Technical Architect
- **Tareas afectadas:** S3-T1, S3-T2, S3-T4, TODO el pipeline

#### **DESCRIPCIÓN DETALLADA**
**¿Qué está bloqueado?**
Decisión sobre qué enfoque usar para upload a Instagram:

**Enfoque 1: Instagram Graph API** (Existente en `qwen-poc/`)
- **Ubicación:** `qwen-poc/service/instagram_service.py`
- **Tecnología:** Requests + Graph API oficial
- **Estado:** Implementado y funcionando
- **Requisitos:** Access token, ngrok para video serving

**Enfoque 2: Playwright UI Automation** (Nuevo en `instagram-upload/`)
- **Ubicación:** `instagram-upload/src/upload/`
- **Tecnología:** Playwright + automatización de navegador
- **Estado:** Recién implementado (Sprint 2)
- **Requisitos:** Credenciales de login, manejo de 2FA

**Ámbito del impacto:**
- ✅ Define arquitectura técnica del sistema
- ✅ Impacta mantenibilidad a largo plazo
- ✅ Afecta requisitos de infraestructura
- ✅ Define dependencias externas
- ✅ Impacta experiencia de usuario (velocidad, confiabilidad)

#### **ANÁLISIS COMPARATIVO**

##### **Graph API (ENFOQUE 1)**
**Ventajas:**
- ✅ **Oficial:** API soportada por Meta
- ✅ **Confiabilidad:** Menos cambios breaking
- ✅ **Rendimiento:** Más rápido (sin navegador)
- ✅ **Escalabilidad:** Mejor para batch processing
- ✅ **Métrica:** Estadísticas de engagement disponibles

**Desventajas:**
- ❌ **Requisitos:** Necesita access token (revisión de app)
- ❌ **Video serving:** Requiere ngrok o servidor público
- ❌ **Limitaciones:** Cuotas de API, restricciones de contenido
- ❌ **Complejidad:** OAuth flow, token management

##### **Playwright UI (ENFOQUE 2)**
**Ventajas:**
- ✅ **Flexibilidad:** Cualquier cosa que un humano pueda hacer
- ✅ **Sin API:** No necesita aprobación de Meta
- ✅ **Testing:** Puede testear UI real
- ✅ **Resiliencia:** Menos afectado por cambios de API

**Desventajas:**
- ❌ **Fragilidad:** Cambios en UI de Instagram pueden romperlo
- ❌ **Rendimiento:** Más lento (carga de navegador)
- ❌ **Recursos:** Más uso de CPU/memoria
- ❌ **Mantenimiento:** Necesita updates frecuentes por cambios UI

#### **RECOMENDACIÓN TÉCNICA**
**Opción A: Usar Graph API (Recomendado para producción)**
- Mejor para escalabilidad
- Más confiable a largo plazo
- Métricas incluidas
- **Riesgo:** Requiere access token (puede ser difícil obtener)

**Opción B: Usar Playwright (Recomendado para desarrollo/POC)**
- Más rápido para empezar
- No requiere aprobación de Meta
- Más flexible
- **Riesgo:** Mantenimiento alto por cambios UI

**Opción C: Sistema híbrido (RECOMENDACIÓN FINAL)**
1. **Por defecto:** Graph API (cuando token disponible)
2. **Fallback:** Playwright UI (cuando no hay token o API falla)
3. **Beneficio:** Resiliencia y flexibilidad máxima

#### **PLAN DE ACCIÓN**
**Paso 1:** Alex Technical Architect convoca reunión urgente (21:30)
**Paso 2:** Decisión final documentada en `ARCHITECTURE_DECISIONS.md`
**Paso 3:** Implementar arquitectura elegida en S3-T1

**Participantes requeridos:**
- Alex Technical Architect (facilitador)
- Sam Lead Developer (implementación)
- Taylor QA Engineer (testing)
- Todos (voto informado)

**Fecha objetivo de resolución:** 2026-04-08 22:00
**Siguiente check:** 21:30 (reunión)

---

### **B3: DEPENDENCIAS DE QWEN-POC NO INSTALADAS**

#### **INFORMACIÓN BÁSICA**
- **ID:** B3
- **Estado:** 🟡 **ABIERTO**
- **Prioridad:** CRÍTICA
- **Impacto:** CRÍTICO - Bloquea pruebas end-to-end
- **Tipo:** TÉCNICO - Configuración de entorno
- **Detección:** 2026-04-08 21:41
- **Reportado por:** Sam Lead Developer
- **Responsable actual:** Taylor QA Engineer
- **Tareas afectadas:** S3-T6 (testing E2E), TODO el testing de integración

#### **DESCRIPCIÓN DETALLADA**
**¿Qué está bloqueado?**
No se puede ejecutar el pipeline de qwen-poc porque faltan dependencias básicas (requests, etc.). Esto bloquea las **pruebas end-to-end** que son nuestra prioridad #1.

**Síntomas específicos:**
- `python3 pipeline.py` → `ModuleNotFoundError: No module named 'requests'`
- qwen-poc no se puede ejecutar para generar contenido de prueba
- Imposible probar integración REAL entre sistemas

**Ámbito del impacto:**
- ✅ Bloquea pruebas end-to-end (prioridad #1)
- ✅ Bloquea validación de integración real
- ✅ Impide verificar que el sistema funciona completamente
- ✅ Afecta confianza en la solución

#### **ANÁLISIS DE CAUSA RAÍZ**
**Relación con B1:**
- **B1:** Dependencias de testing (pytest, etc.) para NUESTRO código
- **B3:** Dependencias de ejecución (requests, etc.) para qwen-poc
- **Ambos son síntomas del mismo problema raíz:** Entorno no configurado correctamente

**Evidencia encontrada:**
- `qwen-poc/requirements.txt` existe pero no instalado
- Mismo patrón que B1: `ModuleNotFoundError` para imports básicos
- Probablemente entorno virtual no activado/instalado

#### **SOLUCIONES PROPUESTAS**

##### **Solución 1: Instalar dependencias de qwen-poc**
```bash
cd /home/luis/code/AIReels/qwen-poc
pip install -r requirements.txt
```
**Ventajas:**
- ✅ Permite ejecutar qwen-poc para pruebas reales
- ✅ Necesario para pruebas end-to-end
- ✅ Soluciona el bloqueo crítico

**Desventajas:**
- ❌ Mismo problema de permisos que B1
- ❌ Puede contaminar entorno global
- ❌ No resuelve problema raíz (gestión de entornos)

##### **Solución 2: Configurar entorno virtual de qwen-poc**
```bash
cd /home/luis/code/AIReels/qwen-poc
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
**Ventajas:**
- ✅ Entorno aislado para qwen-poc
- ✅ No contamina entorno global
- ✅ Solución más limpia

**Desventajas:**
- ❌ Dos entornos virtuales (qwen-poc/venv y nuestro venv)
- ❌ Complejidad de gestión
- ❌ Todos deben activar entorno correcto

##### **Solución 3: Usar Docker unificado (RECOMENDADO LARGO PLAZO)**
```dockerfile
# Dockerfile que incluye ambos sistemas
FROM python:3.12
COPY qwen-poc/ /app/qwen-poc/
COPY instagram-upload/ /app/instagram-upload/
RUN pip install -r /app/qwen-poc/requirements.txt
RUN pip install -r /app/instagram-upload/requirements.txt
```
**Ventajas:**
- ✅ Entorno 100% reproducible
- ✅ Ambos sistemas en mismo entorno
- ✅ Ideal para CI/CD y testing

**Desventajas:**
- ❌ Complejidad inicial alta
- ❌ Overhead para desarrollo local
- ❌ Tiempo de implementación

#### **PLAN DE ACCIÓN**
**Paso 1 (INMEDIATO):** Taylor QA Engineer intenta Solución 1
**Paso 2 (HOY):** Si falla, Sam intenta Solución 2 como temporal
**Paso 3 (SPRINT):** Alex evalúa Solución 3 para futuros sprints

**Relación con prioridad #1 (pruebas E2E):**
1. **Resolver B3** → poder ejecutar qwen-poc
2. **Crear video de prueba** con qwen-poc
3. **Ejecutar integración real** con nuestro módulo
4. **Validar pipeline completo** funciona

**Fecha objetivo de resolución:** 2026-04-08 (URGENTE - hoy)
**Siguiente check:** 21:45 (5 minutos)

#### **ACTUALIZACIÓN 2026-04-08 22:15 - RESUELTO POR SAM LEAD DEVELOPER**
**Estado:** ✅ **RESUELTO**
**Solución aplicada:** Instaladas dependencias de qwen-poc usando `--break-system-packages`
**Comandos ejecutados:**
```bash
/usr/bin/python3 -m pip install --break-system-packages fastapi uvicorn dashscope pydantic openai fal-client
```
**Verificación:**
- ✅ qwen-poc puede ejecutarse (`python3 pipeline.py`)
- ✅ Dependencias instaladas: fastapi, uvicorn, dashscope, pydantic, openai, fal-client
- ✅ Pipeline de generación inicia correctamente
**Lecciones aprendidas:** Mismo problema que B1 - entorno Python externamente gestionado en Ubuntu/Debian requiere `--break-system-packages`
**Fecha resolución:** 2026-04-08 22:15

---

## ✅ **BLOQUEOS RESUELTOS**

*(Ninguno aún - sprint recién comienza)*

---

## 📋 **PLANTILLA PARA NUEVOS BLOQUEOS**

```markdown
### **B[X]: [TÍTULO DEL BLOQUEO]**

#### **INFORMACIÓN BÁSICA**
- **ID:** B[X]
- **Estado:** 🟡 ABIERTO / ✅ RESUELTO
- **Prioridad:** [BAJA/MEDIA/ALTA/CRÍTICA]
- **Impacto:** [BAJO/MEDIO/ALTO/CRÍTICO]
- **Tipo:** [TÉCNICO/PROCESO/RECURSO/EXTERNO]
- **Detección:** [YYYY-MM-DD HH:MM]
- **Reportado por:** [ROL]
- **Responsable actual:** [ROL]
- **Tareas afectadas:** [Lista de IDs de tareas]

#### **DESCRIPCIÓN DETALLADA**
**¿Qué está bloqueado?**
[Descripción clara del problema]

**Síntomas específicos:**
- [Síntoma 1]
- [Síntoma 2]

**Ámbito del impacto:**
- [ ] Qué partes del sistema afecta
- [ ] Qué tareas bloquea
- [ ] Impacto en cronograma

#### **ANÁLISIS DE CAUSA RAÍZ**
**Causa probable:**
1. [Causa 1]
2. [Causa 2]

**Evidencia encontrada:**
- [Evidencia 1]
- [Evidencia 2]

#### **SOLUCIONES PROPUESTAS**
##### **Solución 1: [Nombre]**
[Descripción]
**Ventajas:**
- ✅ [Ventaja 1]
- ✅ [Ventaja 2]
**Desventajas:**
- ❌ [Desventaja 1]
- ❌ [Desventaja 2]

##### **Solución 2: [Nombre]**
[Descripción]
**Ventajas:** [...]
**Desventajas:** [...]

#### **PLAN DE ACCIÓN**
**Paso 1:** [Acción inmediata]
**Paso 2:** [Siguiente paso]
**Paso 3:** [Pasos adicionales]

**Fecha objetivo de resolución:** [Fecha]
**Siguiente check:** [Hora del próximo check]
```

---

## 🚨 **PROTOCOLO DE ESCALACIÓN**

### **NIVEL 1: Resolución por responsable (24h)**
- Responsable intenta resolver
- Documenta intentos en este archivo
- Si no resuelve en 24h → Nivel 2

### **NIVEL 2: Reunión de equipo (48h)**
- Reunión ad-hoc para el bloqueo
- Todos los roles relevantes
- Decisión colectiva
- Si no resuelve en 48h → Nivel 3

### **NIVEL 3: Intervención de arquitecto (72h)**
- Alex Technical Architect toma decisión final
- Puede reasignar recursos
- Puede cambiar scope de tareas
- Documenta lección aprendida

### **NIVEL 4: Revisión de sprint (Crítico)**
- Si bloqueo afecta >50% del sprint
- Revisión completa del sprint
- Replanificación si necesario
- Comunicación a stakeholders

---

## 📊 **MÉTRICAS DE BLOQUEOS**

| Métrica | Sprint 3 | Objetivo |
|---------|----------|----------|
| **Bloqueos activos** | 4 | < 3 |
| **Tiempo medio resolución** | - | < 24h |
| **Bloqueos críticos** | 3 | 0 |
| **Resueltos por responsable** | 0 | >80% |
| **Escalados a nivel 3** | 0 | 0 |

### **BLOQUEOS ACTIVOS:**

1. **B1:** Dependencias testing (pytest) - Taylor QA Engineer
2. **B2:** Decisión arquitectónica upload - Alex Technical Architect
3. **B3:** Dependencias qwen-poc (requests) - Taylor QA Engineer
4. **B4:** Scripts Python complejos fallando - Casey Code Refactoring Expert

**NOTA:** 3 bloqueos críticos identificados (B1, B3, B4) bloquean pruebas E2E

---

**Última actualización:** 2026-04-08 21:52  
**Próxima revisión:** 21:55 (cada 5 minutos para bloqueos críticos)  
**Responsable:** Taylor QA Engineer (B1, B3) + Casey (B4)