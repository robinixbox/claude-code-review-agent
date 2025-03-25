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

Exécutez le script principal:

```bash
python claude_code_reviewer.py
```

Le script vous demandera:
1. L'URL du dépôt GitHub à analyser (ex: https://github.com/username/repository)
2. Le nom du fichier ou du dossier à examiner

L'agent va alors:
1. Récupérer la structure du dépôt GitHub
2. Identifier les fichiers correspondant à votre recherche
3. Analyser chaque fichier à l'aide de l'API Claude
4. Générer des recommandations d'amélioration et du code optimisé
5. Afficher les résultats dans le terminal
6. Exporter les résultats dans Notion (si configuré)

## ⏱️ Temps d'exécution

Le temps d'exécution varie en fonction de la taille et de la complexité du code, ainsi que du nombre de fichiers à analyser:

- Fichier simple (100-200 lignes): 1-2 minutes
- Dossier avec plusieurs fichiers: 5-15 minutes selon le nombre de fichiers
- Projet entier: 15-60 minutes selon la taille du projet

L'agent analyse les fichiers un par un, ce qui permet d'obtenir des premiers résultats rapidement même pour des projets plus grands.

## 🧩 Structure du projet

```
claude-code-review-agent/
├── claude_code_reviewer.py    # Script principal
├── .env.example               # Exemple de configuration des clés API
├── requirements.txt           # Dépendances du projet
└── README.md                  # Documentation
```

## 🔍 Comment ça marche ?

1. **Récupération de la structure du dépôt** : L'agent commence par récupérer la structure du dépôt GitHub et crée des chemins complets pour chaque fichier.

2. **Analyse du contenu** : Pour chaque fichier, l'agent utilise l'API GitHub pour récupérer le contenu.

3. **Revue du code** : L'agent Claude analyse chaque fichier et propose des améliorations basées sur les meilleures pratiques de développement.

4. **Exportation des résultats** : Les résultats sont affichés dans la console et peuvent être exportés vers Notion (si configuré).

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
