# Instagram Upload Service - Módulo de Desarrollo

**Estado:** 🚀 INICIO DE DESARROLLO  
**Fecha inicio:** 2026-04-08  
**Duración estimada:** 27 días  
**Equipo asignado:** AIReels Development Team

## 📋 Resumen del Proyecto

Sistema de upload automático a Instagram Reels usando **Playwright** para automatización del navegador (NO Graph API). Incluye soporte completo para **autenticación de dos factores (2FA)** con pausa para entrada manual del usuario.

### 🎯 Objetivo Principal
Automatizar el proceso completo de publicación de videos generados por AIReels a Instagram Reels, reduciendo el tiempo manual de 5+ minutos a segundos.

### 🔧 Tecnologías Principales
- **Playwright Python:** Automatización del navegador
- **Celery:** Tareas asíncronas para uploads
- **Redis:** Broker para colas de mensajes
- **PostgreSQL:** Almacenamiento de estado y metadata
- **Pytest:** Framework de testing

## 🚀 Comenzar el Desarrollo

### Paso 1: Configuración Inicial
```bash
# 1. Crear y configurar entorno
cd /home/luis/code/AIReels
./scripts/setup_instagram_config.sh

# 2. Editar credenciales (IMPORTANTE: NO commitar)
nano .env.instagram
# Configurar:
# INSTAGRAM_USERNAME=fiestacotoday
# INSTAGRAM_PASSWORD=f4vU+PtT.WUyzqN
# INSTAGRAM_ENABLE_2FA=true

# 3. Instalar dependencias
pip install playwright pytest pytest-playwright celery redis
playwright install chromium

# 4. Probar configuración
python scripts/test_instagram_login.py
# La aplicación se detendrá para solicitar código 2FA de 6 dígitos
```

### Paso 2: Estructura del Proyecto
```bash
# Crear estructura del módulo
mkdir -p instagram-upload/src/{auth,upload,core}
mkdir -p instagram-upload/tests/{unit,integration,e2e}
mkdir -p instagram-upload/{scripts,documentation}

# Inicializar módulo
touch instagram-upload/src/__init__.py
touch instagram-upload/src/auth/__init__.py
touch instagram-upload/src/upload/__init__.py
touch instagram-upload/src/core/__init__.py
```

### Paso 3: Primer Commit
```bash
# Solo después de tener tests básicos
git checkout -b feature/instagram-upload
git add instagram-upload/
git commit -m "feat: Initialize Instagram Upload Service module structure"
```

## 📁 Estructura del Módulo

```
instagram-upload/
├── src/                          # Código fuente
│   ├── auth/                     # Autenticación y sesión
│   │   ├── browser_service.py    # Gestión browser Playwright
│   │   ├── login_manager.py      # Login con soporte 2FA
│   │   └── cookie_manager.py     # Persistencia de cookies
│   ├── upload/                   # Upload y publicación
│   │   ├── video_uploader.py     # Automatización UI upload
│   │   ├── metadata_handler.py   # Caption, hashtags, ubicación
│   │   └── publisher.py          # Confirmación publicación
│   └── core/                     # Núcleo del sistema
│       ├── retry_manager.py      # Exponential backoff
│       ├── error_handler.py      # Manejo CAPTCHA/errores
│       └── scheduler.py          # Tareas Celery
├── tests/                        # Tests automatizados
│   ├── unit/                     # Tests unitarios
│   ├── integration/              # Tests integración
│   └── e2e/                      # Tests end-to-end
├── scripts/                      # Scripts utilitarios
├── documentation/                # Documentación
└── README.md                     # Este archivo
```

## 👥 Roles y Responsabilidades

### Main Developer
- Implementar funcionalidad principal
- Aplicar principios SOLID/DRY
- Crear tests unitarios básicos
- **Primera tarea:** Sistema de login con 2FA

### QA Automation
- Diseñar estrategia de testing
- Implementar tests de integración y E2E
- Validar cobertura > 85%
- **Primera tarea:** Setup ambiente testing

### Documentator
- Documentar código y APIs
- Crear guías de usuario
- Mantener documentación actualizada
- **Primera tarea:** Documentar estructura del módulo

### Refactor Developer
- Mejorar calidad código existente
- Aplicar principios SOLID/DRY
- Reducir deuda técnica
- **Primera tarea:** Revisar código inicial

## ⚠️ Reglas Estrictas

### 1. No Commit Sin Tests
```bash
# Pre-commit hook verificará:
# - Tests para código nuevo
# - Cobertura > 80%
# - Todos los tests pasan

# Si falla, commit será bloqueado
```

### 2. Proceso de 2FA
```python
# Patrón obligatorio para manejo de 2FA
def handle_two_factor():
    """Maneja autenticación de dos factores."""
    try:
        # Intentar login normal
        return login()
    except TwoFactorRequiredError:
        # Pausar para entrada manual del usuario
        print("🔢 Código 2FA requerido (6 dígitos)")
        code = input("Ingresa código: ").strip()
        
        if len(code) != 6 or not code.isdigit():
            raise Invalid2FACodeError("Código debe ser 6 dígitos")
            
        return login_with_2fa(code)
```

### 3. Code Review Obligatorio
1. **Main Developer:** Implementa + tests unitarios
2. **QA Automation:** Valida tests y cobertura
3. **Documentator:** Revisa documentación
4. **Refactor Developer:** Sugiere mejoras código
5. **Arquitecto:** Aprobación final

## 📅 Timeline del Sprint 1 (Días 1-5)

### Día 1: Setup y Configuración
- [ ] Configurar `.env.instagram` con credenciales
- [ ] Probar login con script existente
- [ ] Instalar todas las dependencias
- [ ] Crear estructura básica del módulo

### Día 2: Sistema de Login
- [ ] Implementar `browser_service.py`
- [ ] Implementar `login_manager.py` con 2FA
- [ ] Crear tests unitarios para auth
- [ ] Documentar proceso de login

### Día 3: Persistencia de Sesión
- [ ] Implementar `cookie_manager.py`
- [ ] Guardar/recuperar cookies de sesión
- [ ] Tests para persistencia
- [ ] Documentar seguridad de cookies

### Día 4: Manejo de Errores
- [ ] Implementar `error_handler.py`
- [ ] Manejo de CAPTCHAs y bloqueos
- [ ] Tests para errores comunes
- [ ] Documentar troubleshooting

### Día 5: Integración y Demo
- [ ] Integrar componentes auth
- [ ] Demo de login funcional con 2FA
- [ ] Sprint review y retrospectiva
- [ ] Planificación sprint 2

## 🐛 Debugging y Troubleshooting

### Problemas Comunes

#### 1. Login falla
```bash
# Verificar credenciales
cat .env.instagram | grep INSTAGRAM_

# Probar manualmente
python scripts/test_instagram_login.py

# Revisar logs
tail -f logs/instagram_automation.log
```

#### 2. 2FA no funciona
- Verificar que código sea de 6 dígitos
- Comprobar que no esté expirado (60 segundos)
- Revisar screenshot en `./logs/2fa_error.png`

#### 3. Playwright no inicia
```bash
# Reinstalar browsers
playwright install --force chromium

# Verificar dependencias
pip list | grep playwright
```

## 📞 Soporte y Comunicación

### Canales de Comunicación
- **Slack:** `#instagram-upload-dev`
- **GitHub:** Branch `feature/instagram-upload`
- **Daily Standup:** 9:30 AM Google Meet
- **Urgencias:** `@here` en Slack

### Responsables
- **Technical Lead:** Arquitecto
- **Development Lead:** Main Developer
- **Quality Lead:** QA Automation
- **Documentation Lead:** Documentator

### Recursos
- **Documentación completa:** `/templates/` directory
- **Propuesta técnica:** `templates/instagram_upload_proposal.md`
- **Plan de testing:** `templates/instagram_upload_testing_plan.md`
- **Plan de documentación:** `templates/instagram_upload_documentation_plan.md`

## ✅ Checklist de Inicio

### Antes de Comenzar
- [ ] Credenciales configuradas en `.env.instagram`
- [ ] Playwright y dependencias instaladas
- [ ] Estructura de directorios creada
- [ ] Branch `feature/instagram-upload` creada

### Primeras Tareas
- [ ] Login básico funcionando
- [ ] Manejo de 2FA implementado
- [ ] Tests unitarios creados
- [ ] Documentación inicial escrita

### Verificación Diaria
- [ ] Todos los tests pasan
- [ ] Cobertura > 80% para código nuevo
- [ ] Código sigue principios SOLID
- [ ] Documentación actualizada

---

**¡COMIENZA EL DESARROLLO!** 🚀

**Próximo checkpoint:** Demo de login funcional en 2 días  
**Objetivo Sprint 1:** Sistema de auth completo con 2FA  
**Responsable:** Main Developer (coordinación inicial)

*Última actualización: 2026-04-08*  
*Estado del proyecto: ACTIVO - FASE DE DESARROLLO*