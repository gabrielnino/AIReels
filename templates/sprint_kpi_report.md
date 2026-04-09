# Reporte de KPIs - Sprint [Número]

**Sprint:** [Fechas del sprint]  
**Equipo:** AIReels Development Team  
**Fecha del Reporte:** [Fecha]  
**Preparado por:** [Responsable]

## 1. Resumen Ejecutivo

### 1.1 Estado General del Sprint
| Métrica | Valor | Tendencia | Análisis |
|---------|-------|-----------|----------|
| **Sprint Completion Rate** | [X]% | [▲/▼/→] | [Análisis breve] |
| **Velocity** | [X] pts | [▲/▼/→] | [Análisis breve] |
| **Spillover Rate** | [X]% | [▲/▼/→] | [Análisis breve] |
| **Lead Time Promedio** | [X] días | [▲/▼/→] | [Análisis breve] |

### 1.2 Logros Principales
- [ ] Logro 1
- [ ] Logro 2
- [ ] Logro 3

### 1.3 Desafíos Identificados
- [ ] Desafío 1
- [ ] Desafío 2
- [ ] Desafío 3

## 2. KPIs de Entrega (Delivery)

### 2.1 Velocity del Equipo
| Sprint | Story Points Planificados | Story Points Completados | Velocity | Variación |
|--------|---------------------------|--------------------------|----------|-----------|
| Sprint [N-2] | [X] | [Y] | [Z] pts | - |
| Sprint [N-1] | [X] | [Y] | [Z] pts | [Δ]% |
| **Sprint [N]** | **[X]** | **[Y]** | **[Z] pts** | **[Δ]%** |

**Análisis:** [Explicación del desempeño de velocity]

### 2.2 Sprint Completion Rate
| Categoría | Total | Completadas | % Completado |
|-----------|-------|-------------|--------------|
| **Todas las Tareas** | [X] | [Y] | [Z]% |
| **Historias de Usuario** | [X] | [Y] | [Z]% |
| **Bugs** | [X] | [Y] | [Z]% |
| **Tareas Técnicas** | [X] | [Y] | [Z]% |

**Fórmula:** `(Tareas Completadas / Total Tareas) × 100`

**Análisis:** [Explicación de completion rate]

### 2.3 Spillover Rate
| Sprint | Tareas Planificadas | Tareas Spillover | Spillover Rate |
|--------|---------------------|------------------|----------------|
| Sprint [N-1] | [X] | [Y] | [Z]% |
| **Sprint [N]** | **[X]** | **[Y]** | **[Z]%** |

**Fórmula:** `(Tareas Spillover / Tareas Planificadas) × 100`

**Análisis:** [Explicación de spillover]

### 2.4 Lead Time
| Percentil | Lead Time (días) | Interpretación |
|-----------|------------------|----------------|
| **50% (Mediana)** | [X] | Tiempo típico de entrega |
| **85%** | [X] | Tiempo para mayoría de tareas |
| **95%** | [X] | Casos excepcionales |
| **Promedio** | [X] | Media aritmética |

**Fórmula:** `Fecha Entrega - Fecha Creación Tarea`

**Distribución:**
```
< 1 día:  [X]% de tareas
1-3 días: [X]% de tareas
4-7 días: [X]% de tareas
> 7 días: [X]% de tareas
```

### 2.5 Cycle Time
| Percentil | Cycle Time (días) | Interpretación |
|-----------|-------------------|----------------|
| **50% (Mediana)** | [X] | Desarrollo típico |
| **85%** | [X] | Mayoría de desarrollos |
| **95%** | [X] | Casos complejos |
| **Promedio** | [X] | Media aritmética |

**Fórmula:** `Fecha Completado - Fecha Inicio Desarrollo`

**Análisis:** [Comparación con lead time y eficiencia]

## 3. KPIs de Calidad de Código

### 3.1 Code Churn
| Componente | Líneas Añadidas | Líneas Eliminadas | Líneas Modificadas | Code Churn |
|------------|-----------------|-------------------|-------------------|------------|
| **instagram-upload/** | [X] | [Y] | [Z] | [C]% |
| **qwen-poc/** | [X] | [Y] | [Z] | [C]% |
| **shared/** | [X] | [Y] | [Z] | [C]% |
| **Total** | **[X]** | **[Y]** | **[Z]** | **[C]%** |

**Fórmula:** `(Líneas Eliminadas + Modificadas) / (Añadidas + Eliminadas + Modificadas) × 100`

**Interpretación:**
- **< 10%:** Estable, poco refactor
- **10-30%:** Refactor saludable
- **> 30%:** Alta inestabilidad, posible deuda técnica

### 3.2 PR Cycle Time
| Percentil | PR Cycle Time (horas) | Interpretación |
|-----------|----------------------|----------------|
| **50% (Mediana)** | [X] | Tiempo típico de PR |
| **85%** | [X] | Mayoría de PRs |
| **95%** | [X] | PRs problemáticos |
| **Promedio** | [X] | Media aritmética |

**Fórmula:** `Fecha Merge - Fecha Creación PR`

**Distribución por tamaño:**
```
Small PRs (< 100 líneas): [X] horas
Medium PRs (100-500): [X] horas
Large PRs (> 500): [X] horas
```

### 3.3 PR Size
| Estadística | Líneas Cambiadas | Archivos Cambiados |
|-------------|------------------|-------------------|
| **Mínimo** | [X] | [Y] |
| **Máximo** | [X] | [Y] |
| **Promedio** | [X] | [Y] |
| **Mediana** | [X] | [Y] |

**Distribución de tamaño:**
```
Micro (< 10 líneas): [X]% de PRs
Small (10-100): [X]% de PRs
Medium (100-500): [X]% de PRs
Large (> 500): [X]% de PRs
```

### 3.4 Review Time
| Estadística | Tiempo (horas) | Comentarios por PR |
|-------------|----------------|-------------------|
| **Promedio** | [X] | [Y] |
| **Mediana** | [X] | [Y] |
| **Mínimo** | [X] | [Y] |
| **Máximo** | [X] | [Y] |

**Fórmula:** `Fecha Primer Comment - Fecha Creación PR` (para primer review)

**Análisis:** [Eficiencia del proceso de review]

### 3.5 Build Success Rate
| Sprint | Total Builds | Builds Exitosos | Success Rate |
|--------|--------------|-----------------|--------------|
| Sprint [N-1] | [X] | [Y] | [Z]% |
| **Sprint [N]** | **[X]** | **[Y]** | **[Z]%** |

**Desglose por causa de fallo:**
- Tests fallidos: [X]% de fallos
- Linting errors: [X]% de fallos
- Dependencies: [X]% de fallos
- Infrastructure: [X]% de fallos

## 4. KPIs de Testing

### 4.1 Cobertura de Tests
| Componente | Cobertura Inicial | Cobertura Final | Δ | Objetivo |
|------------|-------------------|-----------------|---|----------|
| **instagram-upload/** | [X]% | [Y]% | [Z]% | 85% |
| **qwen-poc/** | [X]% | [Y]% | [Z]% | 80% |
| **Total** | **[X]%** | **[Y]%** | **[Z]%** | **82%** |

### 4.2 Calidad de Tests
| Métrica | Valor | Objetivo | Estado |
|---------|-------|----------|--------|
| **Test Pass Rate** | [X]% | 100% | [✅/⚠️/❌] |
| **Test Execution Time** | [X] min | < 10 min | [✅/⚠️/❌] |
| **Flaky Tests** | [X] | 0 | [✅/⚠️/❌] |
| **Test Debt** | [X] pts | 0 | [✅/⚠️/❌] |

## 5. KPIs de Documentación

### 5.1 Documentation Coverage
| Tipo Documentación | Total Elementos | Documentados | % Cobertura |
|--------------------|-----------------|--------------|-------------|
| **Funciones/Métodos** | [X] | [Y] | [Z]% |
| **Clases** | [X] | [Y] | [Z]% |
| **APIs/Endpoints** | [X] | [Y] | [Z]% |
| **Guías de Usuario** | [X] | [Y] | [Z]% |
| **Total** | **[X]** | **[Y]** | **[Z]%** |

**Fórmula:** `(Elementos Documentados / Total Elementos) × 100`

### 5.2 Documentation Freshness
| Documento | Última Actualización | Cambios en Código | Estado |
|-----------|----------------------|-------------------|--------|
| **README.md** | [Fecha] | [X] cambios | [✅ Actualizado/⚠️ Desactualizado] |
| **API Documentation** | [Fecha] | [X] cambios | [✅ Actualizado/⚠️ Desactualizado] |
| **Architecture Docs** | [Fecha] | [X] cambios | [✅ Actualizado/⚠️ Desactualizado] |
| **User Guides** | [Fecha] | [X] cambios | [✅ Actualizado/⚠️ Desactualizado] |

**Freshness Score:** `[X]%`  
**Fórmula:** `(Documentos Actualizados / Total Documentos) × 100`

## 6. KPIs por Rol

### 6.1 Main Developer
| Métrica | Developer 1 | Developer 2 | Developer 3 | Promedio |
|---------|-------------|-------------|-------------|----------|
| **Story Points Completados** | [X] | [X] | [X] | [X] |
| **PRs Creados** | [X] | [X] | [X] | [X] |
| **Code Review Participation** | [X]% | [X]% | [X]% | [X]% |
| **Bugs Introducidos** | [X] | [X] | [X] | [X] |

### 6.2 QA Automation
| Métrica | Valor | Objetivo | Estado |
|---------|-------|----------|--------|
| **Tests Escritos** | [X] | [Y] | [✅/⚠️/❌] |
| **Bugs Encontrados** | [X] | - | - |
| **Test Automation Rate** | [X]% | 95% | [✅/⚠️/❌] |
| **False Positive Rate** | [X]% | < 5% | [✅/⚠️/❌] |

### 6.3 Documentator
| Métrica | Valor | Objetivo | Estado |
|---------|-------|----------|--------|
| **Documentación Creada** | [X] páginas | [Y] | [✅/⚠️/❌] |
| **Documentación Actualizada** | [X] documentos | [Y] | [✅/⚠️/❌] |
| **Feedback Score** | [X]/5 | 4+ | [✅/⚠️/❌] |
| **Gaps Identificados** | [X] | - | - |

### 6.4 Refactor Developer
| Métrica | Valor | Objetivo | Estado |
|---------|-------|----------|--------|
| **Code Smells Resueltos** | [X] | [Y] | [✅/⚠️/❌] |
| **Deuda Técnica Reducida** | [X] pts | [Y] | [✅/⚠️/❌] |
| **Complexidad Reducida** | [X]% | [Y]% | [✅/⚠️/❌] |
| **Tests Mejorados** | [X] | [Y] | [✅/⚠️/❌] |

## 7. Análisis de Desempeño

### 7.1 Fortalezas
1. **Fortaleza 1:** [Descripción con datos]
2. **Fortaleza 2:** [Descripción con datos]
3. **Fortaleza 3:** [Descripción con datos]

### 7.2 Áreas de Mejora
1. **Área 1:** [Descripción con datos y root cause]
   - **Acción propuesta:** [Acción específica]
   - **Responsable:** [Rol/Persona]
   - **Deadline:** [Fecha]

2. **Área 2:** [Descripción con datos y root cause]
   - **Acción propuesta:** [Acción específica]
   - **Responsable:** [Rol/Persona]
   - **Deadline:** [Fecha]

3. **Área 3:** [Descripción con datos y root cause]
   - **Acción propuesta:** [Acción específica]
   - **Responsable:** [Rol/Persona]
   - **Deadline:** [Fecha]

### 7.3 Riesgos Identificados
| Riesgo | Probabilidad | Impacto | Mitigación | Owner |
|--------|--------------|---------|------------|-------|
| [Riesgo 1] | [Alta/Media/Baja] | [Alto/Medio/Bajo] | [Acción] | [Persona] |
| [Riesgo 2] | [Alta/Media/Baja] | [Alto/Medio/Bajo] | [Acción] | [Persona] |

## 8. Plan de Acción para el Siguiente Sprint

### 8.1 Objetivos de Mejora
1. **Objetivo 1:** [Descripción SMART]
   - **Métrica a mejorar:** [KPI específico]
   - **Target:** [Valor objetivo]
   - **Acciones:** [Lista de acciones]

2. **Objetivo 2:** [Descripción SMART]
   - **Métrica a mejorar:** [KPI específico]
   - **Target:** [Valor objetivo]
   - **Acciones:** [Lista de acciones]

### 8.2 Focus del Próximo Sprint
- **Prioridad 1:** [Tema/Feature principal]
- **Prioridad 2:** [Mejoras de proceso/deuda]
- **Prioridad 3:** [Innovación/experimentación]

### 8.3 Compromisos del Equipo
| Rol | Compromiso para el próximo sprint |
|-----|-----------------------------------|
| **Main Developer** | [Compromiso específico] |
| **QA Automation** | [Compromiso específico] |
| **Documentator** | [Compromiso específico] |
| **Refactor Developer** | [Compromiso específico] |
| **Arquitecto** | [Compromiso específico] |

## 9. Apéndice: Datos Crudos

### 9.1 Tareas del Sprint
| ID | Título | Tipo | Story Points | Estado | Lead Time | Cycle Time | Comentarios |
|----|--------|------|--------------|--------|-----------|------------|-------------|
| [ID] | [Título] | [Tipo] | [X] | [Estado] | [X] días | [X] días | [Comentarios] |

### 9.2 PRs del Sprint
| PR # | Título | Autor | Tamaño | Cycle Time | Review Time | Comentarios |
|------|--------|-------|--------|------------|-------------|-------------|
| [#] | [Título] | [Autor] | [X] líneas | [X] horas | [X] horas | [Comentarios] |

### 9.3 Builds del Sprint
| Build # | Estado | Duración | Causa de Fallo (si aplica) | Branch |
|---------|--------|----------|----------------------------|--------|
| [#] | [✅/❌] | [X] min | [Causa] | [Branch] |

---

**Próxima Revisión de KPIs:** [Fecha del próximo sprint review]  
**Responsable del Seguimiento:** [Nombre/Rol]  
**Aprobado por:** [Arquitecto/Team Lead]  

*Este reporte se generará automáticamente al final de cada sprint.*