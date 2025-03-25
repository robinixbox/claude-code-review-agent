#!/usr/bin/env python
"""
Script d'analyse automatique amélioré des pull requests
Permet l'exécution via GitHub Actions lors d'une PR
Inclut des logs détaillés et une meilleure gestion des erreurs
"""
import os
import sys
import argparse
import requests
import json
import logging
import time
import traceback
from datetime import datetime

# Configuration du logger
def setup_logger(debug_mode=False):
    """Configure le système de logging"""
    level = logging.DEBUG if debug_mode else logging.INFO
    
    # Format des logs
    log_format = '%(asctime)s [%(levelname)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configuration du logger
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Logger personnalisé pour les étapes importantes
    logger = logging.getLogger('pr_review')
    
    # Afficher la configuration
    if debug_mode:
        logger.debug("🔍 Mode DEBUG activé")
    
    return logger

def parse_args():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description="Agent d'analyse automatique amélioré des pull requests")
    parser.add_argument("--repo", type=str, required=True, help="Nom du dépôt au format 'owner/repo'")
    parser.add_argument("--pr", type=int, required=True, help="Numéro de la pull request")
    parser.add_argument("--debug", action="store_true", help="Activer le mode débogage (plus de logs)")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout pour les appels API en secondes (défaut: 60)")
    return parser.parse_args()

def verify_environment_vars(logger):
    """Vérifie que les variables d'environnement nécessaires sont définies"""
    required_vars = ["ANTHROPIC_API_KEY", "GITHUB_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        return False
    
    optional_vars = ["GITHUB_USERNAME", "NOTION_API_KEY", "NOTION_PAGE_ID"]
    for var in optional_vars:
        if not os.getenv(var):
            logger.warning(f"⚠️ Variable d'environnement optionnelle non définie: {var}")
    
    logger.info("✅ Variables d'environnement vérifiées")
    return True

def get_pr_files(owner, repo, pr_number, github_token, timeout=60, logger=None):
    """Récupère la liste des fichiers modifiés dans une PR"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {"Authorization": f"token {github_token}"}
    
    try:
        logger.info(f"🔍 Récupération des fichiers de la PR #{pr_number}...")
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        elapsed_time = time.time() - start_time
        
        files = response.json()
        logger.info(f"✅ {len(files)} fichier(s) trouvé(s) dans la PR (en {elapsed_time:.2f} secondes)")
        
        if logger and logger.level == logging.DEBUG:
            for file in files:
                logger.debug(f"📄 Fichier: {file['filename']} ({file['status']})")
        
        return files
    except requests.exceptions.Timeout:
        if logger:
            logger.error(f"❌ Timeout lors de la récupération des fichiers de la PR (> {timeout}s)")
        return []
    except requests.exceptions.RequestException as e:
        if logger:
            logger.error(f"❌ Erreur lors de la récupération des fichiers de la PR: {e}")
        return []
    except Exception as e:
        if logger:
            logger.error(f"❌ Erreur inattendue lors de la récupération des fichiers de la PR: {e}")
            if logger.level == logging.DEBUG:
                logger.debug(f"Traceback: {traceback.format_exc()}")
        return []

def post_pr_comment(owner, repo, pr_number, comment, github_token, timeout=60, logger=None):
    """Publie un commentaire sur une pull request"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    
    try:
        logger.info(f"📝 Publication du commentaire sur la PR #{pr_number}...")
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        elapsed_time = time.time() - start_time
        
        logger.info(f"✅ Commentaire publié avec succès (en {elapsed_time:.2f} secondes)")
        return True
    except requests.exceptions.Timeout:
        if logger:
            logger.error(f"❌ Timeout lors de la publication du commentaire (> {timeout}s)")
        return False
    except requests.exceptions.RequestException as e:
        if logger:
            logger.error(f"❌ Erreur lors de la publication du commentaire: {e}")
            if response := getattr(e, 'response', None):
                logger.error(f"   Code d'erreur: {response.status_code}")
                try:
                    error_detail = response.json()
                    logger.error(f"   Détails: {error_detail}")
                except:
                    logger.error(f"   Réponse: {response.text}")
        return False
    except Exception as e:
        if logger:
            logger.error(f"❌ Erreur inattendue lors de la publication du commentaire: {e}")
            if logger.level == logging.DEBUG:
                logger.debug(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Fonction principale"""
    # Parse les arguments
    args = parse_args()
    
    # Configure le logger
    logger = setup_logger(args.debug)
    
    # En-tête
    logger.info("=" * 50)
    logger.info("🤖 AGENT D'ANALYSE DES PULL REQUESTS (VERSION AMÉLIORÉE)")
    logger.info("=" * 50)
    
    # Vérifier les variables d'environnement
    if not verify_environment_vars(logger):
        return 1
    
    # Récupérer le token GitHub depuis l'environnement
    github_token = os.getenv("GITHUB_API_KEY")
    if not github_token:
        logger.error("❌ Token GitHub non trouvé. Définissez la variable d'environnement GITHUB_API_KEY.")
        return 1
    
    # Récupérer le propriétaire et le dépôt à partir de l'argument
    try:
        owner, repo = args.repo.split('/')
        logger.info(f"✅ Dépôt: {owner}/{repo}, PR: #{args.pr}")
    except ValueError:
        logger.error("❌ Format de dépôt invalide. Utilisez le format 'owner/repo'.")
        return 1
    
    # Importer les modules nécessaires
    try:
        from claude_code_reviewer import ReviewCrew, create_notion_page
        logger.info("✅ Modules importés avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur d'importation des modules: {e}")
        logger.error("⚠️ Assurez-vous que toutes les dépendances sont installées (pip install -r requirements.txt)")
        return 1
    
    # Récupérer les fichiers modifiés dans la PR
    pr_files = get_pr_files(owner, repo, args.pr, github_token, args.timeout, logger)
    
    if not pr_files:
        logger.error("❌ Aucun fichier trouvé dans la PR ou erreur lors de la récupération.")
        return 1
    
    # Créer une page Notion si les clés API sont configurées
    page_id = None
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    
    if notion_api_key and notion_page_id:
        try:
            logger.info("🔍 Création d'une page Notion...")
            page_id = create_notion_page(project_name=f"{repo} PR #{args.pr}")
            if page_id:
                logger.info(f"✅ Page Notion créée avec l'ID: {page_id}")
            else:
                logger.warning("⚠️ Échec de la création de la page Notion")
        except Exception as e:
            logger.error(f"⚠️ Erreur lors de la création de la page Notion: {e}")
            if args.debug:
                logger.debug(f"Traceback: {traceback.format_exc()}")
    else:
        logger.info("ℹ️ Exportation vers Notion désactivée (clés API manquantes)")
    
    # Filtrer les fichiers Python
    python_files = [file for file in pr_files if file['filename'].endswith('.py') and file['status'] != 'removed']
    
    if not python_files:
        logger.warning("⚠️ Aucun fichier Python trouvé dans la PR.")
        comment = "⚠️ **Revue de code automatique**\n\nAucun fichier Python trouvé dans cette PR. Aucune analyse effectuée."
        post_pr_comment(owner, repo, args.pr, comment, github_token, args.timeout, logger)
        return 0
    
    logger.info(f"✅ {len(python_files)} fichier(s) Python à analyser")
    
    # Préparer le commentaire pour la PR
    review_results = []
    
    # Analyser chaque fichier un par un
    for i, file in enumerate(python_files):
        filename = file['filename']
        logger.info(f"📄 ({i+1}/{len(python_files)}) Analyse de {filename}...")
        
        # Exécuter l'équipe de revue
        start_time = time.time()
        try:
            review_crew = ReviewCrew(owner=owner, repo=repo, page_id=page_id, path=filename)
            result = review_crew.run()
            elapsed_time = time.time() - start_time
            
            # Sauvegarder le résultat
            review_results.append({
                "file": filename,
                "result": result,
                "time": elapsed_time
            })
            
            # Afficher les résultats
            logger.info(f"✅ Revue terminée pour {filename} en {elapsed_time:.2f} secondes")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse de {filename}: {e}")
            if args.debug:
                logger.debug(f"Traceback: {traceback.format_exc()}")
            
            # Ajouter un résultat d'erreur
            review_results.append({
                "file": filename,
                "result": f"Erreur lors de l'analyse: {e}",
                "error": True
            })
    
    # Formater le commentaire pour la PR
    review_comment = "# 🤖 Revue de code automatique\n\n"
    review_comment += f"J'ai analysé {len(python_files)} fichier(s) Python dans cette PR.\n\n"
    
    for result in review_results:
        review_comment += f"## Fichier: `{result['file']}`\n\n"
        
        if result.get('error'):
            review_comment += f"⚠️ {result['result']}\n\n"
        else:
            try:
                # Si le résultat est une chaîne représentant un tableau
                if isinstance(result['result'], str):
                    parsed_result = json.loads(result['result'].replace("'", "\""))
                else:
                    parsed_result = result['result']
                
                if isinstance(parsed_result, list) and len(parsed_result) >= 3:
                    file_path = parsed_result[1]
                    review_text = parsed_result[2]
                    
                    review_comment += f"### Analyse\n\n{review_text}\n\n"
                    if len(parsed_result) >= 4:
                        improved_code = parsed_result[3]
                        review_comment += f"### Code amélioré suggéré\n\n```python\n{improved_code}\n```\n\n"
                else:
                    review_comment += f"⚠️ Format de résultat inattendu\n\n"
            except Exception as e:
                logger.error(f"❌ Erreur lors du traitement du résultat pour {result['file']}: {e}")
                review_comment += f"⚠️ Erreur lors de l'analyse de ce fichier: {e}\n\n"
        
        review_comment += "---\n\n"
    
    review_comment += "\n\n> Cette revue a été générée automatiquement par Claude Code Review Agent."
    review_comment += f"\n> Temps total d'analyse: {sum(r.get('time', 0) for r in review_results):.2f} secondes."
    
    # Publier le commentaire sur la PR
    if post_pr_comment(owner, repo, args.pr, review_comment, github_token, args.timeout, logger):
        logger.info("✅ Commentaire publié sur la PR avec succès!")
    else:
        logger.error("❌ Échec de la publication du commentaire sur la PR.")
        return 1
    
    logger.info("\n✅ Analyse de la PR terminée!")
    if page_id:
        logger.info(f"📝 Les résultats ont été exportés vers Notion")
    
    return 0

if __name__ == "__main__":
    # Capture l'heure de début pour calculer le temps total d'exécution
    start_time = time.time()
    
    # Exécution de la fonction principale avec gestion des exceptions non capturées
    try:
        exit_code = main()
        elapsed_time = time.time() - start_time
        print(f"\n⏱️ Temps total d'exécution: {elapsed_time:.2f} secondes")
        print(f"📅 Terminé le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Arrêt manuel de l'exécution")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erreur non capturée: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
