#!/bin/bash

# Ce script d'initialisation configure les variables d'environnement
# pour l'agent de revue de code Claude

# Création du fichier .env
cat > .env << EOF
# Configuration des clés API
# Remplacez ces valeurs par vos propres clés
ANTHROPIC_API_KEY=your_api_key_here
GITHUB_API_KEY=your_github_token_here
GITHUB_USERNAME=your_github_username

# Notion (optionnel)
NOTION_API_KEY=your_notion_api_key_here
NOTION_PAGE_ID=your_notion_page_id_here
EOF

echo "✅ Fichier .env créé avec succès!"
echo "⚠️ N'oubliez pas de remplacer les valeurs par défaut par vos propres clés."
echo "📝 Pour utiliser les variables d'environnement du système :"
echo "  1. Ouvrez le terminal et exécutez :"
echo "      source setup_env.sh"
echo "  2. Ou modifiez manuellement le fichier .env créé."
