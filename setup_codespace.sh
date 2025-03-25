#!/bin/bash

# Script pour configurer les variables d'environnement manuellement dans Codespace
# Exécutez ce script avec bash setup_codespace.sh

echo "🔧 Configuration des clés API pour l'agent de revue de code Claude"
echo "=============================================================="
echo ""
echo "Veuillez entrer vos clés API (appuyez sur Entrée pour conserver les valeurs par défaut)"

# Demander les clés API
read -p "ANTHROPIC_API_KEY (Claude): " anthropic_key
read -p "GITHUB_API_KEY (Token d'accès personnel): " github_key
read -p "GITHUB_USERNAME (Nom d'utilisateur GitHub): " github_username
read -p "NOTION_API_KEY (Optionnel): " notion_key
read -p "NOTION_PAGE_ID (Optionnel): " notion_page_id

# Utiliser les valeurs par défaut si l'utilisateur n'a rien entré
anthropic_key=${anthropic_key:-$ANTHROPIC_API_KEY}
github_key=${github_key:-$GITHUB_API_KEY}
github_username=${github_username:-$GITHUB_USERNAME}
notion_key=${notion_key:-$NOTION_API_KEY}
notion_page_id=${notion_page_id:-$NOTION_PAGE_ID}

# Créer le fichier .env
cat > .env << EOF
# Configuration des clés API
ANTHROPIC_API_KEY=${anthropic_key}
GITHUB_API_KEY=${github_key}
GITHUB_USERNAME=${github_username}

# Notion (optionnel)
NOTION_API_KEY=${notion_key}
NOTION_PAGE_ID=${notion_page_id}
EOF

echo ""
echo "✅ Fichier .env créé avec succès!"
echo "📝 Vous pouvez maintenant exécuter l'agent de revue de code avec :"
echo "   python claude_code_reviewer.py"
echo ""
echo "💡 Pour tester les GitHub Actions, configurez les mêmes secrets dans votre dépôt GitHub."
echo "   Consultez GITHUB_ACTIONS_SETUP.md pour plus d'informations."
