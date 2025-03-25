# Configuration des GitHub Actions pour l'Agent de Revue de Code

Ce document explique comment configurer les secrets GitHub nécessaires pour permettre l'exécution autonome de l'agent de revue de code via GitHub Actions.

## Configuration des secrets GitHub

Pour utiliser les workflows GitHub Actions, vous devez configurer plusieurs secrets dans votre dépôt. Ces secrets sont utilisés pour stocker en toute sécurité vos clés API et autres informations sensibles.

### Étapes pour configurer les secrets

1. Accédez aux paramètres de votre dépôt sur GitHub
   - Allez sur `https://github.com/username/claude-code-review-agent/settings`
   - Ou cliquez sur l'onglet "Settings" dans votre dépôt

2. Dans le menu latéral, cliquez sur "Secrets and variables" puis "Actions"

3. Cliquez sur le bouton "New repository secret"

4. Configurez les secrets suivants un par un :

   | Nom du secret | Description | Requis |
   |---------------|-------------|--------|
   | `ANTHROPIC_API_KEY` | Votre clé API Claude d'Anthropic | Oui |
   | `GITHUB_API_KEY` | Votre token d'accès personnel GitHub | Oui |
   | `GITHUB_USERNAME` | Votre nom d'utilisateur GitHub | Oui |
   | `NOTION_API_KEY` | Votre clé API Notion | Non |
   | `NOTION_PAGE_ID` | L'ID de votre page Notion | Non |

   Pour chaque secret :
   - Dans le champ "Name", entrez le nom du secret (par exemple, "ANTHROPIC_API_KEY")
   - Dans le champ "Value", entrez la valeur correspondante
   - Cliquez sur "Add secret"

## Paramètres d'autorisation (si nécessaire)

Si vous rencontrez des problèmes de permission avec les actions GitHub, vous devrez peut-être ajuster les paramètres d'autorisation :

1. Dans les paramètres du dépôt, allez dans "Actions" puis "General"
2. Faites défiler jusqu'à "Workflow permissions"
3. Sélectionnez "Read and write permissions"
4. Cochez "Allow GitHub Actions to create and approve pull requests"
5. Cliquez sur "Save"

## Utilisation des workflows

Une fois les secrets configurés, vous pouvez utiliser les workflows GitHub Actions de trois façons :

### 1. Exécution manuelle

1. Allez dans l'onglet "Actions" de votre dépôt
2. Cliquez sur "Code Review Automation" dans la liste des workflows
3. Cliquez sur "Run workflow"
4. Remplissez les champs requis :
   - Entrez l'URL du dépôt à analyser
   - Entrez le chemin du fichier ou du dossier à examiner
5. Cliquez sur "Run workflow"

### 2. Exécution automatique via Pull Request

Le workflow s'exécutera automatiquement lorsque vous ou quelqu'un d'autre ouvrez ou mettez à jour une pull request qui modifie des fichiers Python.

### 3. Exécution programmée

Le workflow s'exécute automatiquement une fois par jour à minuit (00:00 UTC) et analyse le dépôt spécifié dans le fichier `config.json`.

## Vérification des logs

Pour voir les résultats de l'exécution d'un workflow :

1. Allez dans l'onglet "Actions" de votre dépôt
2. Cliquez sur l'exécution de workflow que vous souhaitez examiner
3. Cliquez sur le job "review_code"
4. Développez les étapes pour voir les logs détaillés

## Dépannage

Si vous rencontrez des problèmes avec les workflows GitHub Actions :

- Vérifiez que tous les secrets requis sont correctement configurés
- Assurez-vous que votre token GitHub a les permissions suffisantes
- Vérifiez les logs d'exécution pour identifier les erreurs spécifiques
- Assurez-vous que les modèles Claude spécifiés sont disponibles avec votre abonnement
