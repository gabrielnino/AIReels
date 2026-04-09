# Equipo AIReels

## Roles y Responsabilidades

### Arquitecto
**Responsable:** Alex Technical Architect

#### Responsabilidades Principales:
1. **Diseño de Arquitectura:** Definir la estructura técnica del proyecto
2. **Autorización de Funcionalidades:** Aprobar o rechazar propuestas de desarrollo
3. **Estándares Técnicos:** Establecer y hacer cumplir estándares de código
4. **Revisión de Arquitectura:** Evaluar impactos arquitectónicos de nuevas funcionalidades
5. **Documentación Técnica:** Asegurar documentación adecuada de decisiones arquitectónicas

#### Proceso de Autorización:
1. **Propuesta:** Cualquier nueva funcionalidad requiere una propuesta técnica
2. **Revisión:** El Arquitecto revisa la propuesta considerando:
   - Coherencia con la arquitectura existente
   - Escalabilidad y mantenibilidad
   - Impacto en rendimiento
   - Costos de implementación
3. **Decisión:** El Arquitecto aprueba, rechaza o solicita modificaciones
4. **Documentación:** Todas las decisiones se documentan en `ARCHITECTURE_DECISIONS.md`

#### Poderes de Decisión:
- ✅ Aprobar/rechazar nuevas funcionalidades
- ✅ Definir patrones arquitectónicos a seguir
- ✅ Establecer herramientas y tecnologías
- ✅ Requerir refactorización cuando sea necesario
- ❌ No puede cambiar requisitos de negocio
- ❌ No puede sobreescribir decisiones de producto

---

### QA Automation
**Responsable:** Taylor QA Engineer

#### Responsabilidades Principales:
1. **Diseño de Pruebas:** Crear estrategia de testing para todo el proyecto
2. **Desarrollo de Tests:** Implementar pruebas unitarias, de integración y E2E
3. **Cobertura de Código:** Asegurar cobertura mínima del 80% en código nuevo
4. **Automatización CI/CD:** Integrar tests en pipeline de integración continua
5. **Mantenimiento de Tests:** Actualizar y refactorizar tests existentes
6. **Calidad de Código:** Verificar que todo el código cumple con estándares de calidad

#### Proceso de Testing:
1. **Requisitos de Testing:** Todas las funcionalidades deben incluir requisitos de prueba
2. **Desarrollo en Paralelo:** Los tests se desarrollan junto con la funcionalidad
3. **Criterio de Aceptación:** No se puede mergear código sin tests apropiados
4. **Cobertura Mínima:** 80% para código nuevo, 70% para código existente
5. **Integración Continua:** Todos los tests deben pasar en CI antes de merge

#### Poderes de Decisión:
- ✅ Rechazar PRs sin cobertura de tests adecuada
- ✅ Requerir tests para funcionalidades existentes
- ✅ Definir herramientas y frameworks de testing
- ✅ Establecer métricas de calidad de código
- ❌ No puede cambiar lógica de negocio
- ❌ No puede sobreescribir decisiones de arquitectura

---

### Main Developer
**Responsable:** Sam Lead Developer

#### Responsabilidades Principales:
1. **Desarrollo de Funcionalidades:** Implementar nuevas funcionalidades según especificaciones
2. **Principios SOLID:** Aplicar principios SOLID en todo el código
3. **Best Practices:** Seguir mejores prácticas de desarrollo (clean code, design patterns)
4. **Principio DRY:** Eliminar duplicación de código y promover reutilización
5. **Code Reviews:** Participar activamente en revisiones de código
6. **Refactorización:** Mejorar continuamente la calidad del código existente
7. **Documentación:** Documentar código, APIs y procesos técnicos

#### Principios Técnicos Obligatorios:
1. **SOLID:**
   - **S**ingle Responsibility: Cada clase/modulo una única responsabilidad
   - **O**pen/Closed: Abierto para extensión, cerrado para modificación
   - **L**iskov Substitution: Subtipos reemplazables por sus tipos base
   - **I**nterface Segregation: Interfaces específicas en lugar de generales
   - **D**ependency Inversion: Depender de abstracciones, no de concreciones

2. **DRY (Don't Repeat Yourself):**
   - Extraer lógica duplicada a funciones/módulos reutilizables
   - Configuración centralizada
   - Utilidades compartidas

3. **Clean Code:**
   - Nombres significativos
   - Funciones pequeñas y enfocadas
   - Comentarios solo cuando el código no es auto-explicativo
   - Estructura clara y organizada

#### Proceso de Desarrollo:
1. **Diseño:** Analizar requerimientos y diseñar solución aplicando principios SOLID
2. **Implementación:** Escribir código limpio, testeable y mantenible
3. **Testing:** Crear tests unitarios junto con el desarrollo
4. **Code Review:** Solicitar revisión de pares y arquitecto
5. **Refactor:** Mejorar continuamente el código
6. **Documentación:** Actualizar documentación técnica

#### Poderes de Decisión:
- ✅ Implementar soluciones técnicas dentro del diseño aprobado
- ✅ Sugerir mejoras arquitectónicas basadas en experiencia práctica
- ✅ Definir implementaciones específicas de módulos/funciones
- ❌ No puede cambiar arquitectura sin aprobación
- ❌ No puede omitir principios SOLID/DRY
- ❌ No puede deployar sin aprobación de QA

---

### Documentator
**Responsable:** Jordan Documentation Specialist

#### Responsabilidades Principales:
1. **Documentación Técnica:** Crear y mantener documentación de todas las funcionalidades
2. **Claridad y Consistencia:** Asegurar que toda la documentación sea clara, concisa y consistente
3. **Documentación de Código:** Verificar que el código tenga comentarios y docstrings adecuados
4. **Guías de Usuario:** Crear documentación para usuarios finales
5. **API Documentation:** Documentar endpoints, parámetros y respuestas de APIs
6. **Documentación de Arquitectura:** Mantener diagramas y documentación arquitectónica actualizada
7. **Procesos y Procedimientos:** Documentar procesos de desarrollo, despliegue y operación

#### Estándares de Documentación:
1. **Consistencia:** Mismo tono, formato y estructura en toda la documentación
2. **Claridad:** Lenguaje simple y directo, evitando jerga innecesaria
3. **Completitud:** Documentación exhaustiva que cubra todos los aspectos
4. **Actualización:** Mantener documentación sincronizada con el código
5. **Accesibilidad:** Documentación fácil de encontrar y navegar

#### Tipos de Documentación Requerida:
1. **Documentación de Código:**
   - Docstrings en todas las funciones y clases
   - Comentarios para lógica compleja
   - README por módulo

2. **Documentación Técnica:**
   - Diagramas de arquitectura
   - Diagramas de secuencia
   - Especificaciones técnicas

3. **Documentación de Usuario:**
   - Guías de instalación
   - Guías de uso
   - Tutoriales paso a paso
   - FAQ (Preguntas frecuentes)

4. **Documentación de API:**
   - Especificación OpenAPI/Swagger
   - Ejemplos de requests/responses
   - Códigos de error

#### Proceso de Documentación:
1. **Documentación Simultánea:** La documentación se crea junto con el desarrollo
2. **Revisión de Documentación:** El Documentator revisa toda la documentación
3. **Aprobación:** Documentación debe ser aprobada antes de considerar completa una funcionalidad
4. **Mantenimiento:** Actualización continua según cambios en el código

#### Poderes de Decisión:
- ✅ Rechazar PRs sin documentación adecuada
- ✅ Requerir documentación para funcionalidades existentes
- ✅ Definir estándares y plantillas de documentación
- ✅ Solicitar mejoras en claridad de código/documentación
- ❌ No puede cambiar lógica de negocio
- ❌ No puede sobreescribir decisiones técnicas

---

### Refactor Developer
**Responsable:** Casey Code Refactoring Expert

#### Responsabilidades Principales:
1. **Refactorización Continua:** Mejorar constantemente la calidad del código existente
2. **Aplicación de Principios:** Implementar SOLID, DRY, KISS, YAGNI en código legacy
3. **Detección de Code Smells:** Identificar y corregir malos olores en el código
4. **Mejora de Diseño:** Rediseñar componentes para mejor mantenibilidad y testabilidad
5. **Eliminación de Duplicación:** Consolidar código duplicado en utilidades reutilizables
6. **Optimización de Performance:** Mejorar rendimiento sin cambiar funcionalidad
7. **Mejora de Legibilidad:** Hacer el código más claro y comprensible
8. **Preparación para Tests:** Hacer código legacy más testeable

#### Principios de Refactorización:
1. **SOLID:** Asegurar que todo el código cumple con principios SOLID
2. **DRY:** Eliminar toda duplicación de código y lógica
3. **KISS (Keep It Simple, Stupid):** Simplificar soluciones complejas
4. **YAGNI (You Ain't Gonna Need It):** Eliminar código no utilizado
5. **Boy Scout Rule:** "Dejar el código más limpio de como lo encontraste"
6. **Refactorización Segura:** Cambios que no rompen funcionalidad existente

#### Técnicas de Refactorización a Aplicar:
1. **Extracción de Métodos:** Dividir métodos largos en más pequeños
2. **Extracción de Clases:** Separar responsabilidades en clases distintas
3. **Renombrado:** Usar nombres más descriptivos
4. **Eliminación de Código Muerto:** Remover código no utilizado
5. **Simplificación de Condicionales:** Reducir complejidad ciclomática
6. **Introducción de Patrones:** Aplicar patrones de diseño apropiados
7. **Mejora de Tipado:** Añadir type hints y validaciones
8. **Standardización:** Unificar estilos y convenciones

#### Proceso de Refactorización:
1. **Identificación:** Encontrar áreas que necesitan mejora (code review, análisis estático)
2. **Planificación:** Crear plan de refactorización con estimación de esfuerzo
3. **Aprobación:** Obtener aprobación del Arquitecto para cambios significativos
4. **Implementación:** Realizar refactorización en pasos pequeños y seguros
5. **Testing:** Asegurar que todos los tests pasan después de cada cambio
6. **Documentación:** Actualizar documentación para reflejar cambios
7. **Code Review:** Revisión por Main Developer y QA Automation

#### Reglas de Refactorización:
1. **Tests Primero:** Nunca refactorizar sin tests que verifiquen comportamiento
2. **Pasos Pequeños:** Cambios incrementales y frecuentes
3. **Comunicación:** Notificar al equipo de cambios que afecten su trabajo
4. **Priorización:** Enfocarse en áreas de mayor impacto/riesgo primero
5. **Reversibilidad:** Diseñar cambios que puedan revertirse si es necesario

#### Métricas de Calidad a Mejorar:
- **Complexidad Ciclomática:** Reducir a < 10 por función
- **Líneas por Función:** Máximo 20-30 líneas
- **Acoplamiento:** Minimizar dependencias entre módulos
- **Cohesión:** Maximizar relación entre elementos de un módulo
- **Cobertura de Tests:** Aumentar cobertura de código legacy
- **Deuda Técnica:** Reducir issues reportados por sonarqube/linters

#### Poderes de Decisión:
- ✅ Refactorizar código existente para mejorar calidad
- ✅ Sugerir cambios arquitectónicos basados en problemas identificados
- ✅ Requerir que nuevo código cumpla con estándares de calidad
- ✅ Detener merge de código con malos olores significativos
- ❌ No puede cambiar funcionalidad visible al usuario
- ❌ No puede introducir breaking changes sin aprobación
- ❌ No puede refactorizar código activamente en desarrollo sin coordinación

## Proceso de Desarrollo

### Flujo de Trabajo:
1. **Propuesta:** Desarrollador crea propuesta técnica
2. **Revisión Arquitectónica:** Arquitecto evalúa y aprueba
3. **Implementación:** Desarrollador implementa según diseño aprobado
4. **Revisión de Código:** Incluye verificación de cumplimiento arquitectónico
5. **Despliegue:** Según proceso establecido

### Plantillas:
- [Propuesta Técnica](templates/technical_proposal.md)
- [Solicitud de Autorización](templates/authorization_request.md)

## Miembros del Equipo

| Rol | Nombre | Responsabilidades | Contacto |
|-----|--------|-------------------|----------|
| Arquitecto | Alex Technical Architect | Ver responsabilidades arriba | [Pendiente] |
| QA Automation | Taylor QA Engineer | Ver responsabilidades arriba | [Pendiente] |
| Main Developer | Sam Lead Developer | Ver responsabilidades abajo | [Pendiente] |
| Documentator | Jordan Documentation Specialist | Ver responsabilidades abajo | [Pendiente] |
| Refactor Developer | Casey Code Refactoring Expert | Ver responsabilidades abajo | [Pendiente] |

## Comunicación

- **Reuniones de Arquitectura:** Semanal
- **Canal de Decisión:** #architecture en Slack/Teams
- **Documentación:** Todos los cambios en esta carpeta