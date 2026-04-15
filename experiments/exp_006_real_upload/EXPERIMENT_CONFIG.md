# 🔬 EXPERIMENTO 006: Configuración

## 🎯 OBJETIVO
**Publicar video REAL en Instagram @fiestacotoday**

## 📋 HIPÓTESIS
Usando login tradicional directo (evitando one-tap) + manejo robusto de autenticación + click en "Share", podemos completar el ciclo 100% de publicación.

## 🚀 ESTRATEGIA
1. **Evitar one-tap**: Navegar directamente a `accounts/login/`
2. **Login tradicional**: Campos username/password explícitos
3. **Verificación robusta**: Múltiples indicadores de autenticación
4. **Upload con timeout**: 60 segundos máximo
5. **Click REAL en Share**: Publicación completa
6. **Verificación post-publicación**: Navegar a perfil

## ⚠️ ADVERTENCIAS
- **PUBLICACIÓN REAL**: El video será visible públicamente
- **NO REVERSIBLE**: No se puede deshacer
- **CONFIRMACIÓN REQUERIDA**: Script pide confirmación explícita

## 🎥 VIDEO DISPONIBLE
- `test_video_aireels.mp4` (100KB - video de prueba)

## 📊 MÉTRICAS DE ÉXITO
1. ✅ Autenticación verificada
2. ✅ Upload completado
3. ✅ Click en Share realizado
4. ✅ Timestamp de publicación capturado
5. ✅ Acceso a perfil verificado

## 🔧 CONFIGURACIÓN TÉCNICA
- Navegador: Chromium visible (headless=False)
- Slow-mo: 1500ms (comportamiento humano)
- Timeout: 120 segundos
- User-agent: Mozilla/5.0 (Windows NT 10.0...)

## 📁 OUTPUT ESPERADO
1. Screenshots de cada paso
2. Reporte detallado en `EXPERIMENT_006_REPORT.md`
3. Timestamp de publicación
4. Evidencia de éxito/fallo

---

*Configuración lista para ejecución - 2026-04-14*