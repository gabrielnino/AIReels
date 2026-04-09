# 📋 REGLA FUNDAMENTAL: ACTUALIZACIÓN CONSTANTE DE TAREAS

**Directiva obligatoria para todo el equipo AIReels**
**Última actualización:** 2026-04-08 (Fecha de creación)
**Estado:** ✅ ACTIVA - OBLIGATORIA

---

## 🚨 **ARTÍCULO 1: REGLA BÁSICA (INEGOCIABLE)**

> "**TODO** cambio de estado, avance, bloqueo o descubrimiento  
> **DEBE** documentarse **INMEDIATAMENTE** en el archivo de tareas.  
> **NUNCA** avanzar sin actualizar primero el estado."

### **Consecuencias de no cumplir:**
- ❌ **Primera vez:** Advertencia formal
- ❌ **Segunda vez:** Reunión de corrección con Arquitecto
- ❌ **Tercera vez:** Pérdida temporal de permisos de commit

---

## 📝 **ARTÍCULO 2: QUÉ ACTUALIZAR Y CUÁNDO**

### **2.1 EVENTOS QUE REQUIEREN ACTUALIZACIÓN INMEDIATA:**

| Evento | Estado a usar | Tiempo máximo |
|--------|--------------|---------------|
| **Comenzar tarea** | `IN_PROGRESS` | 5 minutos |
| **Completar tarea** | `COMPLETED` + resultados | 10 minutos |
| **Encontrar bloqueo** | `BLOCKED` + razón | 15 minutos |
| **Cambiar enfoque** | `UPDATED` + nuevo plan | 20 minutos |
| **Descubrir algo** | `DISCOVERY` + impacto | 30 minutos |
| **Recibir feedback** | `FEEDBACK` + acción | 1 hora |

### **2.2 EJEMPLOS PRÁCTICOS:**

```markdown
## 2026-04-08 20:45 - Sam Lead Developer - S3-T1
**Estado:** IN_PROGRESS
**Cambio:** Comenzando integración entre pipelines
**Detalles:** Analizando estructura de qwen-poc/pipeline.py y instagram-upload/
**Siguiente:** Crear diagrama de flujo de datos
**Blocker:** Ninguno
```

```markdown
## 2026-04-08 21:00 - Taylor QA Engineer - S3-T3  
**Estado:** BLOCKED
**Cambio:** Tests fallan por dependencias faltantes
**Detalles:** pytest no instalado en el entorno virtual
**Siguiente:** Instalar pytest y dependencias de testing
**Blocker:** No se puede ejecutar `pip install` sin permisos
```

---

## 🏗️ **ARTÍCULO 3: FORMATO OBLIGATORIO**

### **3.1 ESTRUCTURA MÍNIMA REQUERIDA:**

```markdown
## [YYYY-MM-DD HH:MM] - [ROL] - [TAREA-ID]
**Estado:** [IN_PROGRESS/COMPLETED/BLOCKED/UPDATED/DISCOVERY/FEEDBACK]
**Cambio:** [Una línea describiendo el cambio]
**Detalles:** [3-5 puntos de qué específicamente se hizo/cambió/descubrió]
**Siguiente:** [Acción inmediata siguiente - específica y medible]
**Blocker:** [Si aplica - qué específicamente bloquea el progreso]
**Evidencia:** [Opcional - archivos, logs, screenshots relevantes]
```

### **3.2 EJEMPLO COMPLETO:**

```markdown
## 2026-04-08 21:15 - Jordan Documentation Specialist - S3-T5
**Estado:** COMPLETED
**Cambio:** Documentación de API de integración creada
**Detalles:**
- Documentado formato de metadata entre sistemas
- Creado diagrama de secuencia del flujo completo
- Actualizado README con instrucciones de integración
- Añadidos ejemplos de uso en `examples/integration_example.py`
**Siguiente:** Revisión por parte del Arquitecto técnico
**Blocker:** Ninguno
**Evidencia:** `documentation/INTEGRATION_API.md`, `diagrams/flow_sequence.png`
```

---

## 📊 **ARTÍCULO 4: HERRAMIENTAS Y PROCESOS**

### **4.1 ARCHIVOS DE SEGUIMIENTO OBLIGATORIOS:**

1. **`SPRINT_CURRENT_STATUS.md`** - Estado actual del sprint
2. **`TEAM_TASK_UPDATES.md`** - Actualizaciones individuales del equipo
3. **`BLOCKERS_AND_SOLUTIONS.md`** - Bloqueos y soluciones encontradas
4. **`DISCOVERIES_AND_INSIGHTS.md`** - Descubrimientos importantes

### **4.2 FREQUENCIA DE ACTUALIZACIÓN:**

- **Individual:** Cada 2 horas máximo (o ante cualquier cambio)
- **Equipo:** Revisión colectiva cada 4 horas
- **Sprint:** Actualización completa cada 24 horas

### **4.3 RESPONSABILIDADES POR ROL:**

| Rol | Responsabilidad primaria | Frecuencia mínima |
|-----|-------------------------|-------------------|
| **Arquitecto** | Validar actualizaciones técnicas | Cada 6 horas |
| **Main Developer** | Actualizar progreso de desarrollo | Cada 2 horas |
| **QA Automation** | Actualizar estado de tests | Cada test completado |
| **Documentator** | Actualizar documentación | Cada documento |
| **Refactor Developer** | Actualizar refactorizaciones | Cada módulo |

---

## 🔄 **ARTÍCULO 5: FLUJO DE TRABAJO CON LA REGLA**

### **5.1 CICLO DE ACTUALIZACIÓN:**

```
[INICIO] → Trabajar en tarea → [CAMBIO DETECTADO] → 
→ Actualizar archivo → [VALIDAR FORMATO] → 
→ Continuar trabajo → [PRÓXIMO CAMBIO] → ...
```

### **5.2 CHECKLIST PRE-COMMIT:**

- [ ] ¿Actualicé el estado de mi tarea actual?
- [ ] ¿Documenté cambios específicos realizados?
- [ ] ¿Especificqué la próxima acción?
- [ ] ¿Mencioné bloqueos si existen?
- [ ] ¿El formato cumple con el artículo 3?

### **5.3 CHECKLIST PRE-MEETING:**

- [ ] ¿Todos los miembros actualizaron sus estados?
- [ ] ¿Los bloqueos están documentados?
- [ ] ¿Las soluciones propuestas están registradas?
- [ ] ¿Los descubrimientos están compartidos?

---

## 🚑 **ARTÍCULO 6: SITUACIONES ESPECIALES**

### **6.1 BLOQUEOS CRÍTICOS:**
- **Definición:** Bloqueo que detiene > 2 horas de trabajo
- **Acción:** Notificar inmediatamente vía Slack `@here` + actualizar estado
- **Escalación:** Notificar al Arquitecto en < 30 minutos

### **6.2 DESCUBRIMIENTOS CRÍTICOS:**
- **Ejemplos:** Bug de seguridad, vulnerabilidad, arquitectura incorrecta
- **Acción:** Detener trabajo relacionado + actualizar estado + notificar equipo
- **Prioridad:** Sobre cualquier otra tarea

### **6.3 FALLAS DEL SISTEMA:**
- Si GitHub/Slack/otra herramienta falla:
  1. Documentar en archivo local inmediatamente
  2. Compartir en siguiente canal disponible
  3. Sincronizar cuando sistema vuelva

---

## 📈 **ARTÍCULO 7: MÉTRICAS Y SEGUIMIENTO**

### **7.1 MÉTRICAS A MONITOREAR:**
- **Frecuencia de actualización:** Veces/día que cada rol actualiza
- **Tiempo de detección:** Cuánto tarda en documentarse un bloqueo
- **Calidad de updates:** % de updates que cumplen formato completo
- **Impacto:** Reducción en tiempo perdido por descoordinación

### **7.2 REPORTES AUTOMÁTICOS:**
- **Diario:** Resumen de actividades del equipo
- **Por sprint:** Efectividad de la comunicación
- **Post-mortem:** Lecciones aprendidas sobre actualizaciones

---

## 🏆 **ARTÍCULO 8: BENEFICIOS ESPERADOS**

### **8.1 PARA EL EQUIPO:**
- ✅ **Visibilidad total** del progreso real
- ✅ **Detección temprana** de bloqueos
- ✅ **Coordinación perfecta** entre roles
- ✅ **Historial completo** para post-mortems
- ✅ **Onboarding acelerado** de nuevos miembros

### **8.2 PARA EL PROYECTO:**
- 📉 **Reducción >50%** en tiempo perdido
- 📈 **Aumento >30%** en velocidad de desarrollo
- 🔍 **Transparencia 100%** en estado real
- 🎯 **Enfoque mantenido** en objetivos del sprint

### **8.3 PARA CADA INDIVIDUO:**
- 🛡️ **Protección:** Evita "¿en qué ibas?" moments
- 📚 **Aprendizaje:** Registro de decisiones y porqués
- 🤝 **Colaboración:** Base sólida para pair programming
- 🎖️ **Reconocimiento:** Trabajo visible y documentado

---

## 📋 **ARTÍCULO 9: IMPLEMENTACIÓN INMEDIATA**

### **9.1 ACCIONES REQUERIDAS HOY:**

1. **Todos los miembros:** Leer y confirmar entendimiento de esta directiva
2. **Arquitecto:** Crear archivos de seguimiento iniciales
3. **Main Developer:** Empezar a usar formato en tarea actual
4. **QA Automation:** Añadir check de formato en pre-commit hooks
5. **Documentator:** Agregar esta directiva al onboarding

### **9.2 ARCHIVOS A CREAR INMEDIATAMENTE:**

- [ ] `SPRINT_CURRENT_STATUS.md` - Estado del Sprint 3
- [ ] `TEAM_TASK_UPDATES.md` - Actualizaciones del equipo
- [ ] `BLOCKERS_AND_SOLUTIONS.md` - Bloqueos actuales
- [ ] `DISCOVERIES_AND_INSIGHTS.md` - Descubrimientos del día

### **9.3 PRIMERA ACTUALIZACIÓN OBLIGATORIA:**

**Cada miembro debe hacer su primera actualización en < 30 minutos**  
Usando el formato del Artículo 3, para su tarea actual del Sprint 3.

---

## ⚖️ **ARTÍCULO 10: GOBIERNO Y CUMPLIMIENTO**

### **10.1 COMITÉ DE SEGUIMIENTO:**
- **Presidente:** Arquitecto (Alex Technical Architect)
- **Miembros:** Main Developer, QA Automation
- **Frecuencia:** Revisión diaria de cumplimiento

### **10.2 SANCIONES PROGRESIVAS:**

| Nivel | Sanción | Duración |
|-------|---------|----------|
| **N1:** Primer incumplimiento | Advertencia escrita | - |
| **N2:** Segundo incumplimiento | Reunión correctiva + plan | 1 día |
| **N3:** Tercer incumplimiento | Sin permisos commit | 3 días |
| **N4:** Incumplimiento grave | Revisión de rol en equipo | 1 semana |

### **10.3 RECOMPENSAS POR CUMPLIMIENTO:**
- **Mensual:** Miembro con mejores updates → Reconocimiento público
- **Por sprint:** Equipo con 100% cumplimiento → Celebración equipo
- **Anual:** Historial perfecto → Consideración para promoción

---

## ✅ **FIRMAS Y COMPROMISO**

### **EQUIPO AIReels - COMPROMISO COLECTIVO:**

> "Nos comprometemos a actualizar constantemente nuestro progreso,
> bloqueos y descubrimientos, siguiendo esta directiva al pie de la letra,
> para asegurar la transparencia, coordinación y éxito del proyecto."

**Firmado digitalmente por:**

- **Alex Technical Architect** (Arquitecto): ____________________
- **Sam Lead Developer** (Main Developer): ____________________
- **Taylor QA Engineer** (QA Automation): ____________________
- **Jordan Documentation Specialist** (Documentator): ____________________
- **Casey Code Refactoring Expert** (Refactor Developer): ____________________

**Fecha de efectividad:** 2026-04-08  
**Revisión programada:** 2026-04-15 (1 semana)

---

## 🆘 **CONTACTO Y SOPORTE**

**Para dudas sobre la directiva:**
- Slack: `#process-rules-questions`
- Email: `process-rules@aireels-team.com`
- Responsable: Alex Technical Architect

**Para reportar incumplimientos:**
- Canal privado: Arquitecto + miembro reportado
- Documentar: `COMPLIANCE_REPORTS.md`
- Anónimo: Formulario en intranet (opcional)

---

**✨ RECUERDA: LA MEJOR HERRAMIENTA ES LA QUE SE USA CONSTANTEMENTE**  
**🔄 ACTUALIZAR = VISIBILIDAD = COORDINACIÓN = ÉXITO**