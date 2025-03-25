#!/bin/bash

# Script pour configurer les variables d'environnement à partir des variables système
# Exécutez ce script avec source setup_env.sh

# Vérification des variables système
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "⚠️ La variable ANTHROPIC_API_KEY n'est pas définie dans votre système."
else
  echo "✅ ANTHROPIC_API_KEY trouvée."
fi

if [ -z "$GITHUB_API_KEY" ]; then
  echo "⚠️ La variable GITHUB_API_KEY n'est pas définie dans votre système."
else
  echo "✅ GITHUB_API_KEY trouvée."
fi

if [ -z "$GITHUB_USERNAME" ]; then
  echo "⚠️ La variable GITHUB_USERNAME n'est pas définie dans votre système."
else
  echo "✅ GITHUB_USERNAME trouvée."
fi

# Création du fichier .env à partir des variables système
cat > .env << EOF
# Configuration des clés API
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-sk-ant-api03-placeholder}
GITHUB_API_KEY=${GITHUB_API_KEY:-ghp-placeholder}
GITHUB_USERNAME=${GITHUB_USERNAME:-robinixbox}

# Notion (optionnel)
NOTION_API_KEY=${NOTION_API_KEY:-}
NOTION_PAGE_ID=${NOTION_PAGE_ID:-}
EOF

echo "✅ Fichier .env créé avec succès à partir des variables système!"
echo "📝 Vous pouvez maintenant exécuter l'agent de revue de code avec :"
echo "   python claude_code_reviewer.py"
