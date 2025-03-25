# Agent de Revue de Code avec Claude et CrewAI

Un agent autonome créé avec [CrewAI](https://www.crewai.io/) et l'API Claude d'Anthropic pour automatiser votre workflow de revue de code.

## 🌟 Fonctionnalités

- Analyse automatique d'un dépôt GitHub
- Revue de code intelligente avec recommandations d'amélioration
- Optimisation des performances et des bonnes pratiques
- Intégration simple avec GitHub
- Exportation des résultats dans un document Notion (optionnel)
- Support des projets Python (extensible à d'autres langages)

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

3. Créez un fichier `.env` à la racine du projet avec vos clés API
   ```
   ANTHROPIC_API_KEY=votre_clé_api_claude
   GITHUB_SECRET_KEY=votre_token_github
   NOTION_API_KEY=votre_clé_api_notion  # Optionnel
   ```

## 💻 Utilisation

### Via le script Python

```bash
python review.py
```

### Via le notebook Jupyter

Ouvrez et exécutez le notebook `code_review_agent.ipynb`.

## 🧩 Structure du projet

```
claude-code-review-agent/
├── code_review_agent.ipynb    # Notebook pour exécuter l'agent
├── review.py                  # Script principal pour lancer la revue
├── requirements.txt           # Dépendances du projet
├── .env                       # Fichier de configuration (à créer)
└── README.md                  # Ce fichier
```

## 🔍 Comment ça marche ?

1. **Récupération de la structure du dépôt** : L'agent commence par récupérer la structure du dépôt GitHub et crée des chemins complets pour chaque fichier.

2. **Analyse du contenu** : Pour chaque fichier, l'agent utilise l'API GitHub pour récupérer le contenu.

3. **Revue du code** : L'agent Claude analyse chaque fichier et propose des améliorations.

4. **Exportation des résultats** : Les résultats sont affichés dans la console et peuvent être exportés vers Notion (si configuré).

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
