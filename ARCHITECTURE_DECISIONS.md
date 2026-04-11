# Decisiones Arquitectónicas

Este documento registra las decisiones arquitectónicas importantes tomadas para el proyecto AIReels.

## Formato de Registro

Cada decisión se registra usando el siguiente formato:

### [ADR-001] Título de la Decisión
**Fecha:** YYYY-MM-DD  
**Estado:** [Propuesta / Aprobada / Obsoleta / Reemplazada por ADR-XXX]  
**Decisor:** [Nombre del Arquitecto]  
**Participantes:** [Nombres de participantes en la decisión]

#### Contexto
[Descripción del problema o situación que requiere una decisión]

#### Opciones Consideradas
1. **Opción A:** [Descripción]
   - **Ventajas:** [Lista]
   - **Desventajas:** [Lista]

2. **Opción B:** [Descripción]
   - **Ventajas:** [Lista]
   - **Desventajas:** [Lista]

3. **Opción C:** [Descripción]
   - **Ventajas:** [Lista]
   - **Desventajas:** [Lista]

#### Decisión
[Opción seleccionada y justificación]

#### Consecuencias
- **Positivas:** [Consecuencias esperadas]
- **Negativas:** [Riesgos o desventajas aceptadas]
- **Neutrales:** [Otros impactos]

#### Validación
[Cómo se validará que la decisión fue correcta]

---

## Decisiones Registradas

### [ADR-001] Estructura del Proyecto
**Fecha:** 2026-04-08  
**Estado:** Aprobada  
**Decisor:** [Arquitecto]  
**Participantes:** Equipo inicial

#### Contexto
Necesidad de organizar el proyecto AIReels para desarrollo colaborativo y escalabilidad.

#### Opciones Consideradas
1. **Monorepo simple:** Todo en una sola carpeta
2. **Estructura modular:** Separación por funcionalidades
3. **Microservicios:** Servicios completamente independientes

#### Decisión
Estructura modular con separación clara de responsabilidades:
- `/qwen-poc/` - Backend de generación de imágenes
- `/video-processing/` - Procesamiento de videos
- `/instagram-upload/` - Servicio de auto-upload
- `/shared/` - Utilidades compartidas

#### Consecuencias
- **Positivas:** Mejor organización, reutilización de código, desarrollo paralelo
- **Negativas:** Mayor complejidad inicial, necesidad de gestión de dependencias
- **Neutrales:** Requiere documentación clara de interfaces

#### Validación
- Facilidad de onboarding de nuevos desarrolladores
- Capacidad de desarrollar funcionalidades en paralelo sin conflictos

---

### [ADR-002] Tecnología Principal Backend
**Fecha:** 2026-04-08  
**Estado:** Aprobada  
**Decisor:** [Arquitecto]  
**Participantes:** Equipo técnico

#### Contexto
Selección del stack tecnológico para el backend del proyecto.

#### Opciones Consideradas
1. **Python + FastAPI:** Ya usado en qwen-poc
2. **Node.js + Express:** Más rápido para I/O, ecosistema grande
3. **Go + Gin:** Alto rendimiento, concurrencia nativa

#### Decisión
Python + FastAPI por:
1. Consistencia con el POC existente
2. Amplio soporte para ML/AI
3. Tipado estático con Pydantic
4. Documentación automática con OpenAPI

#### Consecuencias
- **Positivas:** Reutilización de código existente, fácil integración con bibliotecas de IA
- **Negativas:** Rendimiento inferior a Go para ciertas cargas
- **Neutrales:** Curva de aprendizaje para desarrolladores no familiarizados con Python

#### Validación
- Rendimiento bajo carga real
- Facilidad de mantenimiento y extensión

---

### [ADR-003] Gestión de Dependencias
**Fecha:** 2026-04-08  
**Estado:** Aprobada  
**Decisor:** [Arquitecto]  
**Participantes:** Equipo de desarrollo

#### Contexto
Cómo gestionar dependencias de Python de manera reproducible.

#### Opciones Consideradas
1. **requirements.txt:** Formato tradicional
2. **Pipenv:** Gestión moderna con Pipfile
3. **Poetry:** Gestión completa con lock file y publicación

#### Decisión
Poetry para:
1. Lock file preciso para entornos reproducibles
2. Gestión de dependencias de desarrollo y producción
3. Publicación de paquetes futura
4. Resolución de dependencias más robusta

#### Consecuencias
- **Positivas:** Entornos reproducibles, gestión simplificada
- **Negativas:** Curva de aprendizaje, herramienta adicional
- **Neutrales:** Requiere adaptación del equipo

#### Validación
- Builds consistentes en CI/CD
- Sin conflictos de dependencias en desarrollo

---

---
### [ADR-004] Servicio de Generación de Imágenes
**Fecha:** Según código existente  
**Estado:** Implementada  
**Decisor:** Implementación existente  
**Participantes:** Desarrollador original

#### Contexto
Necesidad de generar imágenes usando modelos de IA para los reels.

#### Opciones Consideradas
1. **Alibaba DashScope (Qwen):** API paga con alta calidad
2. **Pollinations AI (Flux):** API gratuita, calidad aceptable
3. **Stable Diffusion local:** Control completo, requerimientos de hardware

#### Decisión
Pollinations AI (Flux) por:
1. Gratuito, sin necesidad de API key
2. Calidad suficiente para POC
3. Simple integración HTTP
4. Soporta custom width/height

#### Consecuencias
- **Positivas:** Costo cero, implementación simple
- **Negativas:** Dependencia externa, calidad limitada vs servicios premium
- **Neutrales:** Posible migración futura a servicio pago

#### Validación
- Imágenes generadas con calidad aceptable para MVP
- Tiempo de respuesta dentro de límites aceptables

---

### [ADR-005] Estructura de Logging
**Fecha:** Según código existente  
**Estado:** Implementada  
**Decisor:** Implementación existente  
**Participantes:** Desarrollador original

#### Contexto
Necesidad de tracking y debugging en servicio de generación de imágenes.

#### Opciones Consideradas
1. **Print statements:** Simple pero no estructurado
2. **Python logging estándar:** Estándar pero verboso
3. **Structlog o similar:** Logging estructurado
4. **Implementación custom:** Control total

#### Decisión
Implementación custom con logger paso a paso (`log.step()`) por:
1. Tracking explícito de entrada/salida/error
2. Información contextual rica
3. Fácil filtrado y análisis
4. Adaptado a flujos de trabajo específicos

#### Consecuencias
- **Positivas:** Logs muy informativos, fácil debugging
- **Negativas:** Dependencia de implementación custom
- **Neutrales:** Requiere aprendizaje de convenciones propias

#### Validación
- Logs proporcionan suficiente contexto para debugging
- No impacta significativamente el performance

---

### [ADR-006] Gestión de Archivos Generados
**Fecha:** Según código existente  
**Estado:** Implementada  
**Decisor:** Implementación existente  
**Participantes:** Desarrollador original

#### Contexto
Cómo almacenar y gestionar imágenes generadas por el sistema.

#### Opciones Consideradas
1. **Base de datos con BLOBs:** Centralizado pero pesado
2. **Sistema de archivos local:** Simple pero no escalable
3. **Almacenamiento en nube (S3-like):** Escalable pero complejo
4. **Híbrido (local + upload):** Balance entre simple y escalable

#### Decisión
Sistema híbrido:
1. Guardar localmente en `outputs/` durante desarrollo
2. UUID como nombres de archivo para evitar colisiones
3. Descarga automática desde URLs generadas
4. Diseñado para migración futura a cloud storage

#### Consecuencias
- **Positivas:** Simple para desarrollo, preparado para escalar
- **Negativas:** Requiere migración futura para producción
- **Neutrales:** Gestión manual de limpieza de archivos

#### Validación
- Archivos se guardan correctamente sin colisiones
- Ruta de migración a cloud storage clara

---

### [ADR-007] Enfoque de Upload a Instagram
**Fecha:** 2026-04-11  
**Estado:** Aprobada (Revisada)  
**Decisor:** Alex Technical Architect  
**Participantes:** Equipo completo de desarrollo

#### Contexto
Necesidad de decidir el enfoque para subir videos a Instagram desde la aplicación AIReels. Existen dos enfoques principales en el códigobase:
1. **Graph API** (en qwen-poc/service/instagram_service.py) - Enfoque oficial de Instagram
2. **Playwright UI** (en instagram-upload/) - Automatización del navegador

**Actualización:** El usuario ha especificado que no se usará Graph API debido a requisitos del proyecto. La decisión se revisa para usar exclusivamente Playwright UI.

#### Opciones Consideradas
1. **Opción A: Graph API exclusivo**
   - **Ventajas:**
     - Oficial y soportado por Instagram
     - Más confiable y estable
     - Mejor rendimiento (sin overhead de navegador)
     - Mejor manejo de errores
   - **Desventajas:**
     - Requiere access token de Instagram
     - Limitaciones de API (rate limits, funcionalidades)
     - Requiere configuración de aplicación en Facebook Developer
     - **NO ES UNA OPCIÓN** según requisitos del usuario

2. **Opción B: Playwright UI exclusivo**
   - **Ventajas:**
     - No requiere API key/token
     - Acceso completo a todas las funcionalidades de la UI
     - Más flexible para cambios en la UI
     - Puede manejar autenticación de usuario normal
     - Ya existe implementación funcional en instagram-upload/
   - **Desventajas:**
     - Alto mantenimiento (frágil ante cambios en UI)
     - Más lento (overhead de navegador)
     - Más propenso a errores (timeouts, selectores rotos)
     - Requiere manejo de sesiones/cookies

3. **Opción C: Enfoque híbrido (Playwright UI por defecto, Graph API como alternativa)**
   - **Ventajas:**
     - Flexibilidad futura
     - Posibilidad de migrar a Graph API si cambian requisitos
   - **Desventajas:**
     - Mayor complejidad
     - Mantenimiento de dos sistemas
     - No necesario según requisitos actuales

#### Decisión
**Opción B: Playwright UI exclusivo** por las siguientes razones:

1. **Requisitos del usuario:** Claramente especificado que no se usará Graph API
2. **Código existente:** Ya tenemos implementación completa en instagram-upload/
3. **Sin dependencias externas:** No requiere aprobación de Facebook Developer
4. **Funcionalidad completa:** Acceso a todas las características de Instagram UI
5. **Mantenibilidad:** Podemos enfocar esfuerzos en una sola implementación

**Implementación:**
1. **Fase 1:** Usar Playwright UI como único enfoque
2. **Fase 2:** Integrar con módulo de integración existente
3. **Fase 3:** Añadir robustez y manejo de errores

#### Consecuencias
- **Positivas:**
  - Cumple requisitos del usuario
  - Utiliza código existente funcional
  - Sin necesidad de configuración compleja de API
  - Acceso completo a funcionalidades de Instagram
- **Negativas:**
  - Mayor fragilidad ante cambios en UI de Instagram
  - Performance más lento por overhead de navegador
  - Requiere mantenimiento continuo de selectores
- **Neutrales:**
  - Configuración basada en archivos .env
  - Necesita navegador instalado (Playwright)

#### Validación
- Tests de integración deben pasar con Playwright
- Sistema debe manejar errores de UI robustamente
- Performance debe ser aceptable para uso productivo
- Debe funcionar con diferentes configuraciones de navegador

---

## Plantilla para Nuevas Decisiones

### [ADR-XXX] Título de la Decisión
**Fecha:** YYYY-MM-DD  
**Estado:** [Propuesta / Aprobada / Obsoleta / Reemplazada por ADR-XXX]  
**Decisor:** [Nombre]  
**Participantes:** [Nombres]

#### Contexto
[Descripción]

#### Opciones Consideradas
1. **Opción A:** [Descripción]
   - **Ventajas:**
   - **Desventajas:**

2. **Opción B:** [Descripción]
   - **Ventajas:**
   - **Desventajas:**

#### Decisión
[Opción seleccionada y justificación]

#### Consecuencias
- **Positivas:**
- **Negativas:**
- **Neutrales:**

#### Validación
[Cómo se validará]