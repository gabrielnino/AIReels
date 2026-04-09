#!/bin/bash
# Script para actualizar nombres del equipo en toda la documentación
# Uso: ./scripts/update_team_names.sh

set -e  # Exit on error

echo "🏷️  Actualización de Nombres del Equipo AIReels"
echo "================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "TEAM.md" ]; then
    echo -e "${RED}❌ Error: Ejecutar desde directorio raíz de AIReels${NC}"
    exit 1
fi

# Crear backup de archivos importantes
echo -e "${BLUE}📦 Creando backup de archivos...${NC}"
BACKUP_DIR="backup_team_names_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp TEAM.md "$BACKUP_DIR/"
cp README.md "$BACKUP_DIR/" 2>/dev/null || true
cp COLLABORATION_PROCESS.md "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✅ Backup creado en: $BACKUP_DIR${NC}"
echo ""

# Mostrar estado actual
echo -e "${YELLOW}📋 NOMBRES ACTUALES DEL EQUIPO:${NC}"
echo "========================================"
grep -A2 "### " TEAM.md | grep -E "(###|Responsable:)" | while read line; do
    if [[ $line == "### "* ]]; then
        echo -e "\n${BLUE}$line${NC}"
    elif [[ $line == "**Responsable:"* ]]; then
        echo "  $line"
    fi
done
echo ""

# Función para preguntar nombre
ask_name() {
    local role=$1
    local current_name=$2
    local suggestion=$3

    echo -e "${YELLOW}🤔 Rol: $role${NC}"
    echo "Nombre actual: $current_name"
    if [ -n "$suggestion" ]; then
        echo "Sugerencia: $suggestion"
    fi
    echo ""

    while true; do
        read -p "Ingresa el nuevo nombre (o presiona Enter para mantener actual): " new_name

        if [ -z "$new_name" ]; then
            echo -e "${BLUE}⚠️  Manteniendo nombre actual: $current_name${NC}"
            new_name="$current_name"
            break
        elif [ "${#new_name}" -lt 2 ]; then
            echo -e "${RED}❌ Nombre demasiado corto. Mínimo 2 caracteres.${NC}"
        elif [ "${#new_name}" -gt 50 ]; then
            echo -e "${RED}❌ Nombre demasiado largo. Máximo 50 caracteres.${NC}"
        else
            echo -e "${GREEN}✅ Nombre aceptado: $new_name${NC}"
            break
        fi
    done

    echo "$new_name"
}

# Obtener nombres actuales
echo -e "${YELLOW}🎯 ACTUALIZACIÓN DE NOMBRES${NC}"
echo "========================================"
echo "Ingresa los nuevos nombres para cada rol."
echo "Presiona Enter para mantener el nombre actual."
echo ""

# Nombres actuales (extraídos de TEAM.md)
architect_current=$(grep -A1 "### Arquitecto" TEAM.md | grep "Responsable:" | cut -d: -f2 | sed 's/\[\|\]//g' | xargs)
maindev_current=$(grep -A1 "### Main Developer" TEAM.md | grep "Responsable:" | cut -d: -f2 | sed 's/\[\|\]//g' | xargs)
qa_current=$(grep -A1 "### QA Automation" TEAM.md | grep "Responsable:" | cut -d: -f2 | sed 's/\[\|\]//g' | xargs)
doc_current=$(grep -A1 "### Documentator" TEAM.md | grep "Responsable:" | cut -d: -f2 | sed 's/\[\|\]//g' | xargs)
refactor_current=$(grep -A1 "### Refactor Developer" TEAM.md | grep "Responsable:" | cut -d: -f2 | sed 's/\[\|\]//g' | xargs)

# Preguntar por cada rol
echo ""
architect_new=$(ask_name "Arquitecto" "$architect_current" "Ej: Alex Technical Architect")
maindev_new=$(ask_name "Main Developer" "$maindev_current" "Ej: Sam Lead Developer")
qa_new=$(ask_name "QA Automation" "$qa_current" "Ej: Taylor QA Engineer")
doc_new=$(ask_name "Documentator" "$doc_current" "Ej: Jordan Documentation Specialist")
refactor_new=$(ask_name "Refactor Developer" "$refactor_current" "Ej: Casey Code Refactoring Expert")

# Mostrar resumen
echo ""
echo -e "${YELLOW}📊 RESUMEN DE CAMBIOS:${NC}"
echo "============================"
echo -e "${BLUE}Arquitecto:${NC} '$architect_current' → '$architect_new'"
echo -e "${BLUE}Main Developer:${NC} '$maindev_current' → '$maindev_new'"
echo -e "${BLUE}QA Automation:${NC} '$qa_current' → '$qa_new'"
echo -e "${BLUE}Documentator:${NC} '$doc_current' → '$doc_new'"
echo -e "${BLUE}Refactor Developer:${NC} '$refactor_current' → '$refactor_new'"
echo ""

# Confirmar cambios
read -p "¿Confirmar estos cambios? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}❌ Cambios cancelados.${NC}"
    exit 0
fi

# Actualizar TEAM.md
echo -e "${BLUE}📝 Actualizando TEAM.md...${NC}"
sed -i "s/Responsable: \[Nombre del Arquitecto\]/Responsable: $architect_new/" TEAM.md
sed -i "s/Responsable: \[Nombre del QA Automation\]/Responsable: $qa_new/" TEAM.md
sed -i "s/Responsable: \[Nombre del Main Developer\]/Responsable: $maindev_new/" TEAM.md
sed -i "s/Responsable: \[Nombre del Documentator\]/Responsable: $doc_new/" TEAM.md
sed -i "s/Responsable: \[Nombre del Refactor Developer\]/Responsable: $refactor_new/" TEAM.md

# Actualizar tabla en TEAM.md
sed -i "s/| Arquitecto | \[Pendiente\] /| Arquitecto | $architect_new /" TEAM.md
sed -i "s/| QA Automation | \[Pendiente\] /| QA Automation | $qa_new /" TEAM.md
sed -i "s/| Main Developer | \[Pendiente\] /| Main Developer | $maindev_new /" TEAM.md
sed -i "s/| Documentator | \[Pendiente\] /| Documentator | $doc_new /" TEAM.md
sed -i "s/| Refactor Developer | \[Pendiente\] /| Refactor Developer | $refactor_new /" TEAM.md
echo -e "${GREEN}✅ TEAM.md actualizado${NC}"

# Actualizar README.md si existe
if [ -f "README.md" ]; then
    echo -e "${BLUE}📝 Actualizando README.md...${NC}"
    sed -i "s/| Arquitecto | \[Pendiente\] /| Arquitecto | $architect_new /" README.md
    sed -i "s/| Main Developer | \[Pendiente\] /| Main Developer | $maindev_new /" README.md
    sed -i "s/| QA Automation | \[Pendiente\] /| QA Automation | $qa_new /" README.md
    sed -i "s/| Documentator | \[Pendiente\] /| Documentator | $doc_new /" README.md
    sed -i "s/| Refactor Developer | \[Pendiente\] /| Refactor Developer | $refactor_new /" README.md
    echo -e "${GREEN}✅ README.md actualizado${NC}"
fi

# Actualizar COLLABORATION_PROCESS.md si existe
if [ -f "COLLABORATION_PROCESS.md" ]; then
    echo -e "${BLUE}📝 Actualizando COLLABORATION_PROCESS.md...${NC}"
    # Reemplazar referencias genéricas
    sed -i "s/El Arquitecto/$architect_new/g" COLLABORATION_PROCESS.md
    sed -i "s/El Main Developer/$maindev_new/g" COLLABORATION_PROCESS.md
    sed -i "s/El QA Automation/$qa_new/g" COLLABORATION_PROCESS.md
    sed -i "s/El Documentator/$doc_new/g" COLLABORATION_PROCESS.md
    sed -i "s/El Refactor Developer/$refactor_new/g" COLLABORATION_PROCESS.md
    echo -e "${GREEN}✅ COLLABORATION_PROCESS.md actualizado${NC}"
fi

# Actualizar otros archivos con [Pendiente]
echo -e "${BLUE}📝 Buscando otros archivos con [Pendiente]...${NC}"
find . -name "*.md" -type f ! -path "./$BACKUP_DIR/*" ! -path "./node_modules/*" ! -path "./.git/*" -exec grep -l "\[Pendiente\]" {} \; | while read file; do
    echo "  Actualizando: $file"
    sed -i "s/\[Nombre del Arquitecto\]/$architect_new/g" "$file"
    sed -i "s/\[Nombre del Main Developer\]/$maindev_new/g" "$file"
    sed -i "s/\[Nombre del QA Automation\]/$qa_new/g" "$file"
    sed -i "s/\[Nombre del Documentator\]/$doc_new/g" "$file"
    sed -i "s/\[Nombre del Refactor Developer\]/$refactor_new/g" "$file"
    sed -i "s/\[Pendiente\]/$architect_new/g" "$file"
    sed -i "s/\[Pendiente\]/$maindev_new/g" "$file"
    sed -i "s/\[Pendiente\]/$qa_new/g" "$file"
    sed -i "s/\[Pendiente\]/$doc_new/g" "$file"
    sed -i "s/\[Pendiente\]/$refactor_new/g" "$file"
done
echo -e "${GREEN}✅ Archivos MD actualizados${NC}"

# Actualizar archivos de templates
echo -e "${BLUE}📝 Actualizando templates...${NC}"
if [ -d "templates" ]; then
    find templates -name "*.md" -type f -exec sed -i "s/\[Nombre del Arquitecto\]/$architect_new/g" {} \;
    find templates -name "*.md" -type f -exec sed -i "s/\[Nombre del Main Developer\]/$maindev_new/g" {} \;
    find templates -name "*.md" -type f -exec sed -i "s/\[Nombre del QA Automation\]/$qa_new/g" {} \;
    find templates -name "*.md" -type f -exec sed -i "s/\[Nombre del Documentator\]/$doc_new/g" {} \;
    find templates -name "*.md" -type f -exec sed -i "s/\[Nombre del Refactor Developer\]/$refactor_new/g" {} \;
    echo -e "${GREEN}✅ Templates actualizados${NC}"
fi

# Crear archivo de registro de cambios
echo -e "${BLUE}📝 Creando registro de cambios...${NC}"
CHANGE_LOG="team_names_changelog_$(date +%Y%m%d).md"
cat > "$CHANGE_LOG" << EOF
# Registro de Cambios - Nombres del Equipo

**Fecha:** $(date +"%Y-%m-%d %H:%M:%S")
**Realizado por:** $(whoami)

## Cambios Realizados

### Nombres Anteriores
- Arquitecto: $architect_current
- Main Developer: $maindev_current
- QA Automation: $qa_current
- Documentator: $doc_current
- Refactor Developer: $refactor_current

### Nombres Nuevos
- **Arquitecto:** $architect_new
- **Main Developer:** $maindev_new
- **QA Automation:** $qa_new
- **Documentator:** $doc_new
- **Refactor Developer:** $refactor_new

### Archivos Actualizados
1. TEAM.md
2. README.md
3. COLLABORATION_PROCESS.md
4. Templates y otros archivos MD

### Notas
Estos nombres serán utilizados en toda la documentación del proyecto
y en las comunicaciones del equipo.

## Próximos Pasos
1. Actualizar perfiles en sistemas de comunicación (Slack, GitHub, etc.)
2. Informar al equipo completo del cambio
3. Actualizar firma de emails si aplica
4. Revisar que todos los documentos reflejen los nuevos nombres

---
*Actualización automática generada por scripts/update_team_names.sh*
EOF

echo -e "${GREEN}✅ Registro creado: $CHANGE_LOG${NC}"

# Mostrar resumen final
echo ""
echo -e "${GREEN}🎉 ¡ACTUALIZACIÓN COMPLETADA!${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}📋 EQUIPO AIReels ACTUALIZADO:${NC}"
echo "----------------------------------------"
echo -e "${BLUE}Arquitecto:${NC}          $architect_new"
echo -e "${BLUE}Main Developer:${NC}      $maindev_new"
echo -e "${BLUE}QA Automation:${NC}       $qa_new"
echo -e "${BLUE}Documentator:${NC}        $doc_new"
echo -e "${BLUE}Refactor Developer:${NC}  $refactor_new"
echo ""
echo -e "${YELLOW}📁 ARCHIVOS ACTUALIZADOS:${NC}"
echo "----------------------------------------"
echo "• TEAM.md"
echo "• README.md"
echo "• COLLABORATION_PROCESS.md"
echo "• Todos los templates/"
echo "• Otros archivos .md del proyecto"
echo ""
echo -e "${YELLOW}🔍 VERIFICACIÓN RÁPIDA:${NC}"
echo "----------------------------------------"
grep -n "Responsable:" TEAM.md
echo ""
echo -e "${YELLOW}🚀 PRÓXIMOS PASOS:${NC}"
echo "----------------------------------------"
echo "1. Revisar los cambios en los archivos"
echo "2. Commit y push de los cambios"
echo "3. Informar al equipo del nuevo naming"
echo "4. Actualizar perfiles en sistemas externos"
echo ""
echo -e "${GREEN}✅ Los nombres del equipo han sido actualizados exitosamente.${NC}"
echo ""
echo -e "${BLUE}💡 Consejo: Ejecuta 'git diff' para ver todos los cambios realizados.${NC}"

# Opción para commit automático
echo ""
read -p "¿Deseas hacer commit de estos cambios? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${BLUE}💾 Haciendo commit de los cambios...${NC}"
    git add TEAM.md README.md COLLABORATION_PROCESS.md templates/*.md 2>/dev/null || true
    git add "$CHANGE_LOG"
    git commit -m "feat: Update team member names

- Arquitecto: $architect_new
- Main Developer: $maindev_new
- QA Automation: $qa_new
- Documentator: $doc_new
- Refactor Developer: $refactor_new

Todos los documentos han sido actualizados con los nuevos nombres."
    echo -e "${GREEN}✅ Commit realizado.${NC}"
    echo -e "${YELLOW}⚠️  Recuerda hacer 'git push' para subir los cambios.${NC}"
fi

echo ""
echo -e "${GREEN}✨ ¡Proceso completado! El equipo ahora tiene nombres oficiales.${NC}"