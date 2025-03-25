# Claude Code Review Agent (Version Améliorée)

Un agent autonome basé sur CrewAI et Claude API pour automatiser la revue de code avec des fonctionnalités de logs étendus et gestion d'erreurs améliorée.

## 🚀 Améliorations apportées

Cette version améliorée comprend plusieurs modifications importantes pour faciliter le débogage et améliorer la robustesse:

1. **Logs détaillés**:
   - Logs formatés avec horodatage et niveau de log
   - Mode DEBUG qui affiche des informations détaillées sur l'exécution
   - Logs des temps d'exécution à chaque étape importante

2. **Gestion d'erreurs renforcée**:
   - Capture et affichage des exceptions avec traçabilité complète
   - Vérification proactive des variables d'environnement
   - Gestion des timeout dans les appels API
   - Messages d'erreur détaillés pour faciliter le diagnostic

3. **Workflow GitHub Actions amélioré**:
   - Étapes clairement identifiées avec ID
   - Options de débogage intégrées
   - Gestion des échecs avec messages informatifs
   - Contrôle des dépendances et de l'environnement

4. **Outils de déploiement et test**:
   - Script `trigger_workflow.py` pour déclencher les workflows sans passer par l'interface GitHub
   - Surveillance des exécutions de workflow en temps réel
   - Options de configuration flexibles

## 📂 Structure des fichiers

- `.github/workflows/code-review-enhanced.yml`: Workflow GitHub Actions amélioré
- `auto_review_enhanced.py`: Version améliorée du script d'exécution autonome
- `pr_review_enhanced.py`: Version améliorée du script d'analyse de Pull Requests
- `trigger_workflow.py`: Outil pour déclencher les workflows via l'API GitHub
- Fichiers originaux toujours disponibles pour référence

## 🔧 Installation

1. Clonez le dépôt:
   ```bash
   git clone https://github.com/robinixbox/claude-code-review-agent.git
   cd claude-code-review-agent
   ```

2. Installez les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez les variables d'environnement:
   ```bash
   cp .env.example .env
   # Modifiez le fichier .env avec vos clés API
   ```

4. Rendez les scripts exécutables:
   ```bash
   chmod +x auto_review_enhanced.py pr_review_enhanced.py trigger_workflow.py
   ```

## 🔄 Utilisation

### Exécution locale

**Analyse d'un fichier ou dossier**:
```bash
./auto_review_enhanced.py --repo https://github.com/username/repository --target path/to/file.py --debug
```

**Analyse d'une Pull Request**:
```bash
./pr_review_enhanced.py --repo username/repository --pr 123 --debug
```

### Déclenchement du workflow GitHub Actions

```bash
./trigger_workflow.py --repo username/repository --workflow code-review-enhanced.yml --repo-url https://github.com/username/repository --target path/to/file.py --debug --wait
```

### Options principales

- `--debug`: Active les logs détaillés pour le débogage
- `--timeout`: Définit le timeout pour les appels API (en secondes)
- `--wait`: Pour `trigger_workflow.py`, attend la fin de l'exécution et affiche le résultat

## 🛡️ Variables d'environnement requises

- `ANTHROPIC_API_KEY`: Clé API pour Claude (Anthropic)
- `GITHUB_API_KEY`: Token d'accès personnel GitHub avec les permissions adéquates

Variables optionnelles:
- `GITHUB_USERNAME`: Nom d'utilisateur GitHub (pour certaines opérations)
- `NOTION_API_KEY`: Clé API Notion (pour l'export des résultats)
- `NOTION_PAGE_ID`: ID de la page Notion où exporter les résultats

## 📊 Sortie des logs

Exemple de logs en mode DEBUG:
```
2025-03-25 20:15:23 [INFO] ================================================== 
2025-03-25 20:15:23 [INFO] 🤖 AGENT AUTONOME DE REVUE DE CODE (VERSION AMÉLIORÉE) 
2025-03-25 20:15:23 [INFO] ================================================== 
2025-03-25 20:15:23 [DEBUG] 🔍 Mode DEBUG activé 
2025-03-25 20:15:23 [INFO] ✅ Variables d'environnement vérifiées 
2025-03-25 20:15:23 [INFO] 🔍 Analyse de l'URL GitHub: https://github.com/robinixbox/claude-code-review-agent 
2025-03-25 20:15:23 [INFO] ✅ Propriétaire: robinixbox, Dépôt: claude-code-review-agent 
2025-03-25 20:15:23 [INFO] ✅ Modules importés avec succès 
2025-03-25 20:15:23 [INFO] 🔍 Récupération de la structure du dépôt robinixbox/claude-code-review-agent... 
2025-03-25 20:15:25 [INFO] ✅ Structure du dépôt récupérée en 2.14 secondes 
...
```

## 🧪 Déboguer le processus

1. Activez le mode DEBUG pour obtenir plus d'informations:
   ```bash
   ./auto_review_enhanced.py --debug ...
   ```

2. Vérifiez les variables d'environnement:
   ```bash
   env | grep ANTHROPIC
   env | grep GITHUB
   ```

3. Utilisez l'option de timeout plus élevée si nécessaire:
   ```bash
   ./pr_review_enhanced.py --timeout 120 ...
   ```

4. Surveillez l'exécution des workflows avec l'option `--wait`:
   ```bash
   ./trigger_workflow.py --wait ...
   ```

## 📋 Conseils d'intégration

- **Automatisation**: Configurez des déclencheurs GitHub Actions pour analyser automatiquement chaque PR
- **Intégration continue**: Ajoutez le workflow à votre pipeline CI/CD existant
- **Notion**: Utilisez l'intégration Notion pour conserver un historique des revues
- **Personnalisation**: Adaptez les messages et formats de sortie à vos besoins

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une PR pour améliorer ce projet.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
