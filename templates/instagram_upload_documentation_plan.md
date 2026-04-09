# Plan de Documentación: Instagram Upload Service

**Responsable:** Documentator
**Funcionalidad:** Auto-upload a Instagram Reels
**Audiencia:** Desarrolladores, Usuarios, Administradores
**Fecha Inicio:** [Fecha después de aprobación]
**Fecha Fin:** [Fecha + 4 días]

## 1. Objetivos de Documentación

### 1.1 Objetivos Generales
- [ ] Documentar completamente la nueva funcionalidad
- [ ] Asegurar claridad y consistencia en toda la documentación
- [ ] Facilitar onboarding de nuevos desarrolladores
- [ ] Proporcionar guías prácticas para usuarios
- [ ] Mantener documentación sincronizada con código

### 1.2 Principios de Calidad
- **Claridad:** Lenguaje simple, evitando jerga innecesaria
- **Consistencia:** Mismo tono, formato y estructura
- **Completitud:** Cubrir todos los aspectos y casos de uso
- **Actualización:** Sincronizada con cada cambio en código
- **Accesibilidad:** Fácil de encontrar y navegar

## 2. Tipos de Documentación Requerida

### 2.1 Documentación de Código
| Documento | Audiencia | Formato | Responsable | Deadline |
|-----------|-----------|---------|-------------|----------|
| Docstrings funciones/clases | Desarrolladores | Google Style | Main Developer + Documentator | Diario |
| Comentarios código complejo | Desarrolladores | Inline comments | Main Developer | Durante desarrollo |
| README módulo instagram-upload | Desarrolladores | Markdown | Documentator | Fase 1 |
| API Reference interna | Desarrolladores | Auto-generado (OpenAPI) | Automático | Post-implementación |

### 2.2 Documentación Técnica
| Documento | Audiencia | Formato | Responsable | Deadline |
|-----------|-----------|---------|-------------|----------|
| Arquitectura del servicio | Desarrolladores, Arquitecto | Mermaid + texto | Documentator | Fase 2 |
| Diagramas de secuencia | Desarrolladores | Mermaid | Documentator | Fase 2 |
| Decisiones técnicas | Equipo técnico | ADR format | Documentator | Fase 3 |
| Especificación de API | Desarrolladores | OpenAPI YAML | Main Developer + Documentator | Fase 3 |

### 2.3 Documentación de Usuario
| Documento | Audiencia | Formato | Responsable | Deadline |
|-----------|-----------|---------|-------------|----------|
| Guía de instalación | Usuarios técnicos | Markdown + bash | Documentator | Fase 4 |
| Guía de configuración | Administradores | YAML examples | Documentator | Fase 4 |
| Tutorial paso a paso | Usuarios finales | Screenshots + pasos | Documentator | Fase 4 |
| FAQ y troubleshooting | Todos | Q&A format | Documentator | Fase 4 |

### 2.4 Documentación Operacional
| Documento | Audiencia | Formato | Responsable | Deadline |
|-----------|-----------|---------|-------------|----------|
| Guía de deploy | DevOps | Bash scripts + config | Documentator | Fase 4 |
| Monitoreo y alertas | SRE | Dashboard config | Documentator | Fase 4 |
| Backup y recovery | Administradores | Procedures | Documentator | Fase 4 |
| Scaling guidelines | Arquitecto, DevOps | Best practices | Documentator | Fase 4 |

## 3. Estructura de Documentación

### 3.1 Directorios de Documentación
```
documentation/
├── instagram-upload/
│   ├── api/
│   │   ├── openapi.yaml
│   │   └── examples/
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── diagrams/
│   │   └── decisions/
│   ├── user-guides/
│   │   ├── installation.md
│   │   ├── configuration.md
│   │   ├── tutorial.md
│   │   └── faq.md
│   ├── operations/
│   │   ├── deployment.md
│   │   ├── monitoring.md
│   │   └── troubleshooting.md
│   └── development/
│       ├── setup.md
│       ├── testing.md
│       └── contributing.md
└── shared/
    └── templates/
```

### 3.2 Integración con Código
```python
# Ejemplo de docstring completo (Google Style)
def upload_video_to_instagram(video_path: str, metadata: InstagramMetadata) -> str:
    """Sube un video a Instagram Reels con metadatos especificados.
    
    Esta función maneja el proceso completo de upload a Instagram:
    1. Validación de video y metadatos
    2. Autenticación con Instagram Graph API
    3. Upload del video file
    4. Aplicación de metadatos (caption, hashtags, etc.)
    5. Confirmación de publicación
    
    Args:
        video_path: Ruta al archivo de video a subir. Debe ser formato
            MP4 o MOV, máximo 90 segundos, máximo 100MB.
        metadata: Objeto InstagramMetadata con información de la publicación.
            Incluye caption, hashtags, ubicación, etc.
    
    Returns:
        Media ID de Instagram para la publicación creada.
    
    Raises:
        ValidationError: Si el video o metadatos no cumplen requisitos.
        AuthenticationError: Si hay problemas con autenticación.
        UploadError: Si falla el upload a Instagram API.
        TimeoutError: Si la operación excede timeout configurado.
    
    Examples:
        >>> metadata = InstagramMetadata(
        ...     caption="Mi primer reel generado con AI!",
        ...     hashtags=["#aireels", "#ai", "#video"],
        ...     location_id="123456789"
        ... )
        >>> media_id = upload_video_to_instagram("/videos/my_reel.mp4", metadata)
        >>> print(f"Video publicado con ID: {media_id}")
    
    Notes:
        - Requiere token de acceso válido de Instagram Graph API.
        - Los videos pueden tardar varios minutos en procesarse en Instagram.
        - Use `check_upload_status()` para monitorear progreso.
    """
    # Implementación
```

## 4. Proceso de Documentación

### 4.1 Flujo de Trabajo
```
[Desarrollo código] → [Docstrings básicos] → [Revisión Documentator] → 
[Mejora documentación] → [Aprobación] → [Integración] → [Publicación]
```

### 4.2 Responsabilidades por Fase
1. **Fase Desarrollo:** Main Developer crea docstrings básicos
2. **Fase Revisión:** Documentator revisa, sugiere mejoras
3. **Fase Mejora:** Documentator expande y estructura documentación
4. **Fase Aprobación:** Main Developer verifica precisión técnica
5. **Fase Integración:** Se integra con documentación existente
6. **Fase Publicación:** Se publica en portal/documentación

### 4.3 Checklist de Revisión
- [ ] Docstrings completos (args, returns, raises, examples)
- [ ] Type hints consistentes
- [ ] Ejemplos prácticos y realistas
- [ ] Sin errores ortográficos/gramaticales
- [ ] Enlaces funcionan correctamente
- [ ] Formato consistente con guías de estilo
- [ ] Información técnica precisa
- [ ] Cubre todos los casos de uso

## 5. Guías Específicas

### 5.1 Guía de Configuración de Instagram Developer
```markdown
# Configuración de Instagram Developer Account

## 1. Prerrequisitos
- Cuenta de Instagram Business o Creator
- Página de Facebook vinculada
- Acceso a Facebook Developer Portal

## 2. Pasos de Configuración

### Paso 1: Crear App en Facebook Developer
1. Acceder a [Facebook Developer](https://developers.facebook.com/)
2. Click en "My Apps" → "Create App"
3. Seleccionar "Business" como tipo
4. Ingresar nombre de app: "AIReels Upload Service"

### Paso 2: Configurar Productos
1. En Dashboard de la app, agregar "Instagram Graph API"
2. Configurar permisos básicos:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`

### Paso 3: Obtener Credenciales
```bash
# Variables de entorno requeridas
INSTAGRAM_APP_ID=tu_app_id_aqui
INSTAGRAM_APP_SECRET=tu_app_secret_aqui
INSTAGRAM_REDIRECT_URI=https://tu-dominio.com/callback
INSTAGRAM_ACCESS_TOKEN=token_largo_aqui
```

### Paso 4: Configurar Webhooks (Opcional)
Para recibir notificaciones de cambios en Instagram API.

## 3. Troubleshooting

### Problema: "App not reviewed for permissions"
**Solución:** Solicitar review en Facebook Developer portal.

### Problema: "Invalid redirect_uri"
**Solución:** Asegurar URI exacto en configuración de Facebook.

### Problema: "Token expired"
**Solución:** Implementar refresh automático con `refresh_token`.
```

### 5.2 Tutorial de Uso
```markdown
# Tutorial: Subir tu Primer Reel Automáticamente

## Objetivo
Subir un video generado por AIReels a Instagram Reels en 5 minutos.

## Duración: 5-10 minutos

### Paso 1: Generar Video
```bash
# Generar video con AIReels
airels generate-video \
  --prompt "paisaje de montaña al atardecer" \
  --duration 30 \
  --output mi_video.mp4
```

### Paso 2: Configurar Metadata
```python
# Crear archivo metadata.json
{
  "caption": "Hermoso atardecer en la montaña generado con IA 🌄",
  "hashtags": ["#aireels", "#ai", "#montaña", "#atardecer"],
  "location": {
    "name": "Montañas Rocosas",
    "id": "123456789"
  },
  "schedule_time": null  # Publicar inmediatamente
}
```

### Paso 3: Ejecutar Upload
```bash
# Subir a Instagram
airels upload-to-instagram \
  --video mi_video.mp4 \
  --metadata metadata.json \
  --account "mi_cuenta_instagram"
```

### Paso 4: Verificar Publicación
```bash
# Verificar estado
airels check-upload-status --media-id [ID_RETORNADO]

# Monitorear en Instagram
# Tu reel debería aparecer en tu perfil en 1-5 minutos
```

## Consejos
- Usa hashtags relevantes pero no más de 10-15
- Programa publicaciones para horarios pico (7-9 PM)
- Revisa analytics después de 24 horas
```

## 6. Automatización de Documentación

### 6.1 Generación Automática
```yaml
# mkdocs.yml
site_name: AIReels Documentation
nav:
  - Home: index.md
  - Instagram Upload:
    - Overview: instagram-upload/overview.md
    - API Reference: instagram-upload/api.md
    - User Guide: instagram-upload/user-guide.md
    - Developer Guide: instagram-upload/developer-guide.md

plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            docstring_style: google
```

### 6.2 Scripts de Validación
```python
#!/usr/bin/env python3
"""
Validador de documentación para Instagram Upload.
"""
import ast
import os
from pathlib import Path

def validate_documentation():
    """Valida que toda la documentación esté completa."""
    issues = []
    
    # Verificar docstrings en código
    code_dir = Path("instagram-upload")
    for py_file in code_dir.rglob("*.py"):
        issues.extend(validate_python_file(py_file))
    
    # Verificar archivos de documentación
    docs_dir = Path("documentation/instagram-upload")
    for doc_file in docs_dir.rglob("*.md"):
        issues.extend(validate_markdown_file(doc_file))
    
    return issues

def validate_python_file(file_path: Path):
    """Valida docstrings en archivo Python."""
    issues = []
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if not ast.get_docstring(node):
                issues.append(f"Missing docstring: {file_path}:{node.lineno} - {node.name}")
    
    return issues
```

## 7. Métricas de Calidad de Documentación

### 7.1 Métricas a Medir
- **Completitud:** % de funciones/clases con docstrings completos
- **Actualización:** Tiempo desde última actualización vs cambios en código
- **Claridad:** Score de legibilidad (Flesch-Kincaid)
- **Utilidad:** Feedback de usuarios/desarrolladores
- **Consistencia:** Uniformidad en formato y estilo

### 7.2 Dashboard de Monitoreo
```
Documentation Quality Dashboard
┌─────────────────────────────────────┐
│ Completitud: 95%  ▲ 2%             │
│ Actualización: 98% ▼ 1%            │
│ Claridad: 8.2/10  ▲ 0.3            │
│ Satisfacción: 4.5/5                │
└─────────────────────────────────────┘
```

## 8. Entregables

### 8.1 Documentos Principales
- [ ] `instagram-upload/README.md` - Overview del módulo
- [ ] `documentation/instagram-upload/api/openapi.yaml` - Especificación API
- [ ] `documentation/instagram-upload/user-guide/` - Guías completas de usuario
- [ ] `documentation/instagram-upload/architecture/` - Diagramas y decisiones
- [ ] `documentation/instagram-upload/operations/` - Guías operacionales

### 8.2 Integraciones
- [ ] Docstrings completos en 100% del código
- [ ] Página en portal de documentación
- [ ] Ejemplos de código en `/examples/`
- [ ] Plantillas reutilizables en `/templates/`

### 8.3 Validaciones
- [ ] Checklist de revisión completado
- [ ] Aprobación de Main Developer
- [ ] Aprobación de Arquitecto
- [ ] Tests de documentación pasan

## 9. Timeline

| Fase | Duración | Actividades | Entregables |
|------|----------|-------------|-------------|
| **Fase 1:** Análisis | 0.5 días | Revisar código, identificar gaps | Gap analysis report |
| **Fase 2:** Docstrings | 1 día | Mejorar docstrings existentes | Código con docstrings completos |
| **Fase 3:** Guías Técnicas | 1 día | Documentar arquitectura, API | Technical documentation |
| **Fase 4:** Guías Usuario | 1 día | Tutoriales, configuración | User documentation |
| **Fase 5:** Integración | 0.5 días | Integrar con doc existente | Portal actualizado |
| **Fase 6:** Validación | 0.5 días | Revisión, correcciones | Final approval |

**Total:** 4.5 días

## 10. Reglas Estrictas

### 10.1 No Commit Sin Documentación
- ❌ **Prohibido:** Commits sin docstrings en funciones nuevas
- ❌ **Prohibido:** Commits que rompan documentación existente
- ❌ **Prohibido:** Commits sin actualizar documentación afectada
- ✅ **Requerido:** Documentator approval para merge de funcionalidades nuevas
- ✅ **Requerido:** Tests de documentación en CI/CD pipeline

### 10.2 Proceso de Aprobación
1. Main Developer implementa con docstrings básicos
2. Documentator revisa y mejora documentación
3. QA Automation verifica ejemplos en documentación
4. Arquitecto aprueba precisión técnica
5. **Solo entonces:** Merge permitido

---

**Responsable:** Documentator  
**Aprobado por:** Arquitecto  
**Fecha:** 2026-04-08