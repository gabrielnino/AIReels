# INSTRUCCIONES PARA SUBIR VIDEO A INSTAGRAM

## PROBLEMA ACTUAL
El código 2FA `688774` ha expirado (los códigos 2FA cambian cada 30 segundos).

## SOLUCIÓN
Necesitas un **código 2FA FRESCO** de tu app de autenticación.

## PASOS:

### 1. OBTENER CÓDIGO 2FA FRESCO
1. Abre tu app de autenticación (Google Authenticator, Authy, etc.)
2. Busca "Instagram" o "fiestacotoday"
3. Copia el código de 6 dígitos que aparece **AHORA MISMO**
4. El código es válido por solo 30 segundos

### 2. ACTUALIZAR ARCHIVO DE CONFIGURACIÓN
Archivo: `/home/luis/code/AIReels/instagram-upload/.env.instagram`

**Línea actual:**
```
INSTAGRAM_2FA_CODE=688774
```

**Cámbiala por:**
```
INSTAGRAM_2FA_CODE=TU_CODIGO_FRESCO
```

Donde `TU_CODIGO_FRESCO` es el código de 6 dígitos de AHORA.

### 3. EJECUTAR SCRIPT
Una vez actualizado el archivo, voy a ejecutar el script que:
1. Hará login con el código 2FA fresco
2. Clickeará en "Trust this device" (ya implementado)
3. Subirá el video `test_video_aireels.mp4`
4. Publicará en Instagram

## RESUMEN DE LO QUE YA ESTÁ IMPLEMENTADO:
- ✅ Login con 2FA mejorado (selectores expandidos)
- ✅ Manejo de "Trust this device"
- ✅ Flujo completo de upload
- ✅ Navegador visible para ver el proceso

## ¿QUÉ CÓDIGO 2FA FRESCO TIENES AHORA?
Por favor, dime el código de 6 dígitos que aparece AHORA en tu app de autenticación para Instagram/fiestacotoday.