# Agent de Revue de Code avec Claude et CrewAI

Un agent autonome créé avec [CrewAI](https://www.crewai.io/) et l'API Claude d'Anthropic pour automatiser votre workflow de revue de code.

## 🌟 Fonctionnalités

- Analyse automatique d'un dépôt GitHub
- Revue de code intelligente avec recommandations d'amélioration
- Optimisation des performances et des bonnes pratiques
- Intégration simple avec GitHub
- Exportation des résultats dans un document Notion (optionnel)
- Support des projets Python (extensible à d'autres langages)
- **Nouveau**: Exécution autonome via GitHub Actions
- **Nouveau**: Revue automatique des Pull Requests

## 🔧 Prérequis

- Python 3.9+ installé sur votre machine
- Clé API Anthropic (Claude)
- Token d'accès personnel GitHub (PAT)
- Clé API Notion (optionnel)

## 🚀 Installation

1. Clonez ce dépôt
   ```bash
   git clone https://github.com/robinixbox/claude-code-review-agent.git
   cd claude-code-review-agent
   ```

2. Installez les dépendances
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez vos clés API
   - Copiez le fichier `.env.example` en `.env`
   - Ajoutez vos clés API dans le fichier `.env`

   ```
   ANTHROPIC_API_KEY=votre_clé_api_claude
   GITHUB_API_KEY=votre_token_github
   GITHUB_USERNAME=votre_nom_utilisateur_github
   NOTION_API_KEY=votre_clé_api_notion  # Optionnel
   NOTION_PAGE_ID=votre_page_id_notion  # Optionnel
   ```

## 💻 Utilisation

### Exécution manuelle

Exécutez le script principal:

```bash
python claude_code_reviewer.py
```

Le script vous demandera:
1. L'URL du dépôt GitHub à analyser (ex: https://github.com/username/repository)
2. Le nom du fichier ou du dossier à examiner

### Exécution autonome

Vous pouvez également utiliser la version automatisée du script:

```bash
python auto_review.py --repo https://github.com/username/repository --target path/to/file
```

Ou avec un fichier de configuration:

```bash
python auto_review.py --config config.json
```

### Exécution avec GitHub Actions

L'agent peut être configuré pour s'exécuter automatiquement via GitHub Actions:

1. **Exécution programmée**: L'agent s'exécute automatiquement une fois par jour pour analyser le code selon la configuration.

2. **Exécution manuelle**: Vous pouvez déclencher l'analyse manuellement depuis l'onglet Actions de GitHub.

3. **Analyse de Pull Request**: L'agent analyse automatiquement les fichiers modifiés dans une PR et ajoute un commentaire avec les résultats.

#### Configuration des Secrets GitHub

Pour utiliser GitHub Actions, vous devez configurer les secrets suivants dans votre dépôt:

1. Allez dans les paramètres du dépôt > Secrets and variables > Actions
2. Ajoutez les secrets suivants:
   - `ANTHROPIC_API_KEY`: Votre clé API Claude
   - `GITHUB_API_KEY`: Votre token d'accès personnel GitHub
   - `GITHUB_USERNAME`: Votre nom d'utilisateur GitHub
   - `NOTION_API_KEY`: Votre clé API Notion (optionnel)
   - `NOTION_PAGE_ID`: L'ID de votre page Notion (optionnel)

## ⏱️ Temps d'exécution

Le temps d'exécution varie en fonction de la taille et de la complexité du code, ainsi que du nombre de fichiers à analyser:

- Fichier simple (100-200 lignes): 1-2 minutes
- Dossier avec plusieurs fichiers: 5-15 minutes selon le nombre de fichiers
- Projet entier: 15-60 minutes selon la taille du projet

L'agent analyse les fichiers un par un, ce qui permet d'obtenir des premiers résultats rapidement même pour des projets plus grands.

## 🧩 Structure du projet

```
claude-code-review-agent/
├── claude_code_reviewer.py    # Script principal interactif
├── auto_review.py             # Script d'exécution autonome
├── pr_review.py               # Script d'analyse des Pull Requests
├── .github/workflows/         # Workflows GitHub Actions
├── config.json                # Configuration par défaut
├── .env.example               # Exemple de configuration des clés API
├── requirements.txt           # Dépendances du projet
└── README.md                  # Documentation
```

## 🔍 Comment ça marche ?

1. **Récupération de la structure du dépôt** : L'agent commence par récupérer la structure du dépôt GitHub et crée des chemins complets pour chaque fichier.

2. **Analyse du contenu** : Pour chaque fichier, l'agent utilise l'API GitHub pour récupérer le contenu.

3. **Revue du code** : L'agent Claude analyse chaque fichier et propose des améliorations basées sur les meilleures pratiques de développement.

4. **Exportation des résultats** : Les résultats sont affichés dans la console, exportés vers Notion (si configuré) ou postés comme commentaires sur les Pull Requests.

### Intégration avec GitHub Actions

Le workflow GitHub Actions permet trois modes de fonctionnement:

1. **Exécution programmée**: Analyse quotidienne du code selon la configuration dans `config.json`.

2. **Exécution manuelle**: Déclenchement manuel avec spécification du dépôt et du chemin à analyser.

3. **Analyse de Pull Request**: Détection automatique des modifications dans une PR et analyse des fichiers Python modifiés.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
