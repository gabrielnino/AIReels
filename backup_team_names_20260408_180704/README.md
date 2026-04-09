# AIReels - Equipo de Desarrollo

## Descripción del Proyecto
AIReels es una plataforma para generación y procesamiento automático de contenido multimedia usando IA. Incluye generación de imágenes, procesamiento de videos, añadido de watermarks y auto-upload a redes sociales.

## Estructura del Equipo

### Roles y Responsabilidades
1. **Arquitecto** - Diseño técnico y aprobación de funcionalidades
2. **Main Developer** - Desarrollo aplicando SOLID, DRY y best practices
3. **QA Automation** - Pruebas automatizadas y calidad de código
4. **Documentator** - Documentación clara y consistente

### Miembros Actuales
| Rol | Nombre | Contacto | Especialidad |
|-----|--------|----------|--------------|
| Arquitecto | [Pendiente] | [Pendiente] | Arquitectura de sistemas, Python, IA |
| Main Developer | [Pendiente] | [Pendiente] | Python, FastAPI, Computer Vision |
| QA Automation | [Pendiente] | [Pendiente] | Testing automatizado, CI/CD |
| Documentator | [Pendiente] | [Pendiente] | Documentación técnica, guías de usuario |

## Documentación del Equipo

### Documentación Esencial
1. **[TEAM.md](TEAM.md)** - Roles, responsabilidades y estructura del equipo
2. **[COLLABORATION_PROCESS.md](COLLABORATION_PROCESS.md)** - Procesos de trabajo y colaboración
3. **[CODING_STANDARDS.md](CODING_STANDARDS.md)** - Estándares de código y mejores prácticas
4. **[DOCUMENTATION_GUIDE.md](DOCUMENTATION_GUIDE.md)** - Guías para documentación
5. **[ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md)** - Decisiones arquitectónicas registradas

### Plantillas
- **[templates/technical_proposal.md](templates/technical_proposal.md)** - Para propuestas técnicas
- **[templates/authorization_request.md](templates/authorization_request.md)** - Para solicitar autorización

## Estructura del Proyecto

### Componentes Principales
```
AIReels/
├── qwen-poc/                 # Backend de generación de imágenes IA
│   ├── main.py              # Punto de entrada FastAPI
│   ├── service/             # Servicios de negocio
│   ├── models/              # Modelos de datos
│   └── utils/               # Utilidades
├── video-processing/         # Procesamiento de videos (por implementar)
├── instagram-upload/         # Auto-upload a Instagram (por implementar)
├── shared/                  # Utilidades compartidas (por implementar)
├── outputs/                 # Archivos generados
└── tests/                   # Tests automatizados
```

### Tecnologías Principales
- **Backend:** Python 3.10+, FastAPI
- **IA/ML:** Alibaba DashScope (Qwen), OpenCV
- **Testing:** pytest, unittest
- **CI/CD:** GitHub Actions
- **Documentación:** MkDocs, OpenAPI

## Proceso de Desarrollo

### Flujo de Trabajo
1. **Propuesta Técnica** → Main Developer crea propuesta
2. **Aprobación Arquitectónica** → Arquitecto revisa y aprueba
3. **Desarrollo** → Main Developer implementa con tests
4. **Documentación** → Documentator verifica y mejora
5. **Code Review** → Revisión por pares y QA
6. **Merge & Deploy** → Integración y despliegue

### Reglas Importantes
- ✅ SOLID y DRY obligatorios en todo el código
- ✅ Cobertura de tests > 80% para código nuevo
- ✅ Documentación completa para cada funcionalidad
- ✅ Aprobación arquitectónica antes de desarrollo
- ✅ Code review por al menos 2 personas antes de merge

## Comunicación y Reuniones

### Canales de Comunicación
- **GitHub Issues/PRs:** Decisiones técnicas y code reviews
- **Slack/Teams:** Comunicación diaria y coordinación
- **Google Meet:** Reuniones formales

### Reuniones Regulares
- **Daily Standup:** 9:30 AM diario (15 min)
- **Reunión de Arquitectura:** Jueves 10:00 AM (1 hora)
- **Planificación Semanal:** Lunes 11:00 AM (1 hora)
- **Retrospectiva Mensual:** Último viernes del mes (1.5 horas)

## Cómo Contribuir

### Para Nuevos Miembros
1. Leer toda la documentación del equipo
2. Revisar arquitectura y decisiones técnicas
3. Estudiar estándares de código
4. Configurar entorno de desarrollo
5. Comenzar con tareas pequeñas bajo supervisión

### Para Desarrollar Nueva Funcionalidad
1. Crear propuesta técnica usando [plantilla](templates/technical_proposal.md)
2. Obtener aprobación del Arquitecto
3. Desarrollar siguiendo [estándares](CODING_STANDARDS.md)
4. Crear tests con cobertura > 80%
5. Documentar según [guía](DOCUMENTATION_GUIDE.md)
6. Solicitar code review a 2 personas
7. Mergear solo después de aprobaciones

### Para Reportar Issues
1. Crear issue en GitHub con plantilla adecuada
2. Clasificar por severidad (P1-P4)
3. Incluir logs, screenshots y pasos para reproducir
4. Asignar al rol correspondiente según [procesos](COLLABORATION_PROCESS.md)

## Entorno de Desarrollo

### Requisitos
- Python 3.10+
- Git
- IDE con soporte para Python (VS Code, PyCharm)
- Cuenta en Alibaba DashScope (para API de IA)

### Configuración Inicial
```bash
# 1. Clonar repositorio
git clone <repository-url>
cd AIReels

# 2. Configurar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Ejecutar tests
pytest

# 6. Ejecutar aplicación
cd qwen-poc
uvicorn main:app --reload
```

## Métricas y Objetivos

### Métricas del Equipo
- **Velocidad:** 20-30 story points por sprint
- **Calidad:** < 5% bugs en producción
- **Cobertura:** > 80% código cubierto por tests
- **Cycle Time:** < 3 días promedio
- **Satisfacción:** > 4/5 en encuestas de equipo

### Objetivos Trimestrales
1. **Q2 2026:** Sistema estable de generación de imágenes
2. **Q3 2026:** Pipeline completo de videos con watermarks
3. **Q4 2026:** Integración con redes sociales y auto-upload

## Recursos Adicionales

### Documentación Externa
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Alibaba DashScope API Docs](https://help.aliyun.com/zh/dashscope/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Pytest Documentation](https://docs.pytest.org/)

### Herramientas Internas
- **CI/CD:** GitHub Actions
- **Monitoring:** Datadog/Sentry
- **Logging:** ELK Stack
- **Documentación:** MkDocs + GitHub Pages

### Contactos Clave
- **Product Owner:** [Nombre] - [email]
- **Tech Lead:** [Nombre] - [email]
- **DevOps:** [Nombre] - [email]

---

**Última actualización:** 2026-04-08  
**Mantener este documento actualizado es responsabilidad de todo el equipo.**  
**Cambios significativos requieren aprobación del Arquitecto.**