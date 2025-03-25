#!/bin/bash

# Script pour exécuter le test de l'agent de revue de code

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Bannière
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  TEST DE L'AGENT DE REVUE DE CODE ${NC}"
echo -e "${BLUE}=================================${NC}"

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 n'est pas installé. Veuillez l'installer pour continuer.${NC}"
    exit 1
fi

# Vérification des variables d'environnement
echo -e "${YELLOW}Vérification des variables d'environnement...${NC}"
missing_vars=0

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}❌ ANTHROPIC_API_KEY non définie${NC}"
    missing_vars=1
else
    echo -e "${GREEN}✓ ANTHROPIC_API_KEY définie${NC}"
fi

if [ -z "$GITHUB_API_KEY" ]; then
    echo -e "${RED}❌ GITHUB_API_KEY non définie${NC}"
    missing_vars=1
else
    echo -e "${GREEN}✓ GITHUB_API_KEY définie${NC}"
fi

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}❌ GITHUB_USERNAME non définie${NC}"
    missing_vars=1
else
    echo -e "${GREEN}✓ GITHUB_USERNAME définie${NC}"
fi

if [ $missing_vars -ne 0 ]; then
    echo -e "${RED}Des variables d'environnement nécessaires sont manquantes.${NC}"
    echo -e "${YELLOW}Vous pouvez les définir avec :${NC}"
    echo "export ANTHROPIC_API_KEY=votre_clé"
    echo "export GITHUB_API_KEY=votre_clé"
    echo "export GITHUB_USERNAME=votre_nom_utilisateur"
    echo -e "${YELLOW}Ou créer un fichier .env à la racine du projet.${NC}"
    exit 1
fi

# Vérification des dépendances Python
echo -e "${YELLOW}Vérification des dépendances Python...${NC}"
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Erreur lors de l'installation des dépendances.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Dépendances installées${NC}"
fi

# Création du répertoire de logs s'il n'existe pas
mkdir -p logs

# Exécution du test
echo -e "${YELLOW}Démarrage du test...${NC}"
echo -e "${BLUE}---------------------------------${NC}"

python3 test_review.py --config test_config.json

if [ $? -eq 0 ]; then
    echo -e "${BLUE}---------------------------------${NC}"
    echo -e "${GREEN}✓ Test terminé avec succès !${NC}"
    echo -e "${YELLOW}Les logs sont disponibles dans le dossier 'logs'.${NC}"
else
    echo -e "${BLUE}---------------------------------${NC}"
    echo -e "${RED}❌ Erreur lors de l'exécution du test.${NC}"
    echo -e "${YELLOW}Consultez les logs dans le dossier 'logs' pour plus de détails.${NC}"
    exit 1
fi

# Fin
echo -e "${BLUE}=================================${NC}"
