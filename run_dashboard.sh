#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════
# 🎓 SAREP: Script de Ejecución del Dashboard
# ═══════════════════════════════════════════════════════════════════════════
# Script para ejecutar el dashboard con configuración optimizada
# y verificar que todos los artefactos necesarios estén disponibles.
# ═══════════════════════════════════════════════════════════════════════════

# Colores para terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎓 SAREP: Dashboard del Tutor - Prototipo Ilustrativo${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# Verificar que estamos en la raíz del proyecto
if [ ! -f "models/xgboost_model.pkl" ]; then
    echo -e "${RED}❌ Error: No se encontraron los artefactos del modelo.${NC}"
    echo -e "${YELLOW}   Asegúrate de ejecutar este script desde la raíz del proyecto.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Artefactos del modelo encontrados${NC}"

# Verificar que Python esté disponible
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 no está disponible${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 disponible${NC}"

# Verificar Streamlit
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Streamlit no está instalado. Instalando...${NC}"
    python3 -m pip install streamlit
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al instalar Streamlit${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Streamlit disponible${NC}"

# Verificar dependencias del dashboard
echo "🔍 Verificando dependencias del dashboard..."

if ! python3 -c "import pandas, numpy, joblib, xgboost, sklearn" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Faltan dependencias. Instalando...${NC}"
    python3 -m pip install pandas numpy scikit-learn xgboost joblib
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Error al instalar dependencias${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Todas las dependencias disponibles${NC}"
echo ""

# Opciones de ejecución
echo -e "${BLUE}═ Configuración de ejecución:${NC}"
echo ""

# Opción 1: Puerto personalizado
PORT="${1:-8501}"
echo "🌐 Puerto: ${PORT}"

# Opción 2: Abrir automáticamente en navegador
BROWSER="--server.headless false"
echo "🌐 Navegador: Automático"

# Opción 3: Modo debug
if [ "$2" = "--debug" ]; then
    DEBUG="--logger.level debug"
    echo "🔍 Modo debug: ACTIVADO"
else
    DEBUG=""
    echo "🔍 Modo debug: Desactivado"
fi

echo ""

# Ejecutar dashboard
echo -e "${BLUE}🚀 Iniciando dashboard...${NC}"
echo -e "${GREEN}> Este proceso no terminará. Cierra con Control+C${NC}"
echo ""

# Comando Streamlit con configuración optimizada
python3 -m streamlit run app/dashboard.py \
    --server.port ${PORT} \
    --server.headless false \
    --browser.gatherUsageStats false \
    ${DEBUG}

echo ""
echo -e "${GREEN}¡Dashboard cerrado correctamente!${NC}"