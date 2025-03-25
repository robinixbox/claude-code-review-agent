#!/usr/bin/env python
"""
Script d'exécution autonome amélioré pour l'agent de revue de code
Permet l'exécution via GitHub Actions ou en ligne de commande
Inclut des logs détaillés et une meilleure gestion des erreurs
"""
import os
import sys
import json
import time
import argparse
import ast
import logging
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
    logger = logging.getLogger('code_review')
    
    # Afficher la configuration
    if debug_mode:
        logger.debug("🔍 Mode DEBUG activé")
    
    return logger

def parse_args():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description="Agent de revue de code autonome amélioré")
    parser.add_argument("--repo", type=str, help="URL du dépôt GitHub à analyser")
    parser.add_argument("--target", type=str, help="Nom du fichier ou du dossier à examiner")
    parser.add_argument("--config", type=str, help="Chemin vers un fichier de configuration JSON")
    parser.add_argument("--debug", action="store_true", help="Activer le mode débogage (plus de logs)")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout pour les appels API en secondes (défaut: 300)")
    return parser.parse_args()

def load_config(config_path, logger):
    """Charge la configuration depuis un fichier JSON"""
    try:
        logger.info(f"📂 Chargement de la configuration depuis {config_path}")
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.debug(f"✅ Configuration chargée: {json.dumps(config, indent=2)}")
        return config
    except FileNotFoundError:
        logger.error(f"❌ Fichier de configuration non trouvé: {config_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"❌ Erreur de format JSON dans le fichier de configuration: {config_path}")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement de la configuration: {e}")
        if logger.level == logging.DEBUG:
            logger.debug(f"Traceback: {traceback.format_exc()}")
        return None

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

def main():
    """Fonction principale"""
    # Parse les arguments
    args = parse_args()
    
    # Configure le logger
    logger = setup_logger(args.debug)
    
    # En-tête
    logger.info("=" * 50)
    logger.info("🤖 AGENT AUTONOME DE REVUE DE CODE (VERSION AMÉLIORÉE)")
    logger.info("=" * 50)
    
    # Vérifier les variables d'environnement
    if not verify_environment_vars(logger):
        return 1
    
    # Charger la configuration depuis un fichier si spécifié
    config = None
    if args.config:
        config = load_config(args.config, logger)
        if not config:
            return 1
    
    # Déterminer l'URL du dépôt et le chemin cible
    repo_url = args.repo if args.repo else (config.get('repo_url') if config else None)
    target_path = args.target if args.target else (config.get('target_path') if config else None)
    
    if not repo_url:
        logger.error("❌ URL du dépôt GitHub non spécifiée. Utilisez --repo ou un fichier de configuration.")
        return 1
    
    if not target_path:
        logger.error("❌ Chemin cible non spécifié. Utilisez --target ou un fichier de configuration.")
        return 1
    
    # Extraire le propriétaire et le dépôt à partir de l'URL GitHub
    try:
        logger.info(f"🔍 Analyse de l'URL GitHub: {repo_url}")
        split_url = repo_url.split('/')
        owner = split_url[3]
        repo = split_url[4].split('.')[0]  # Supprimer l'extension .git si présente
        logger.info(f"✅ Propriétaire: {owner}, Dépôt: {repo}")
    except IndexError:
        logger.error("❌ URL GitHub invalide. Format attendu: https://github.com/username/repository")
        return 1
    
    # Importer les modules nécessaires
    try:
        from claude_code_reviewer import get_file_tree, global_path, create_notion_page, Agents, Tasks, ReviewCrew
        logger.info("✅ Modules importés avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur d'importation des modules: {e}")
        logger.error("⚠️ Assurez-vous que toutes les dépendances sont installées (pip install -r requirements.txt)")
        return 1
    
    # Récupérer la structure arborescente du dépôt
    logger.info(f"🔍 Récupération de la structure du dépôt {owner}/{repo}...")
    start_time = time.time()
    try:
        get_file_tree(owner=owner, repo=repo)
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Structure du dépôt récupérée en {elapsed_time:.2f} secondes")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération de la structure du dépôt: {e}")
        if logger.level == logging.DEBUG:
            logger.debug(f"Traceback: {traceback.format_exc()}")
        return 1
    
    if not global_path:
        logger.error("❌ Impossible de récupérer la structure du dépôt. Vérifiez vos identifiants et l'URL.")
        return 1
    
    # Créer une page Notion si les clés API sont configurées
    page_id = None
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    
    if notion_api_key and notion_page_id:
        try:
            logger.info("🔍 Création d'une page Notion...")
            page_id = create_notion_page(project_name=repo)
            if page_id:
                logger.info(f"✅ Page Notion créée avec l'ID: {page_id}")
            else:
                logger.warning("⚠️ Échec de la création de la page Notion")
        except Exception as e:
            logger.error(f"⚠️ Erreur lors de la création de la page Notion: {e}")
            if logger.level == logging.DEBUG:
                logger.debug(f"Traceback: {traceback.format_exc()}")
    else:
        logger.info("ℹ️ Exportation vers Notion désactivée (clés API manquantes)")
    
    # Importer l'agent de chemin pour trouver les fichiers correspondants
    path_agent = Agents.path_agent()
    path_task = Tasks.get_file_path_task(agent=path_agent, filetree=global_path, user_input=target_path)
    
    logger.info(f"🔍 Recherche des fichiers correspondant à '{target_path}'...")
    try:
        paths_output = path_task.execute()
        logger.debug(f"Résultat brut de la recherche: {paths_output}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la recherche des fichiers: {e}")
        if logger.level == logging.DEBUG:
            logger.debug(f"Traceback: {traceback.format_exc()}")
        return 1
    
    try:
        paths = ast.literal_eval(paths_output)
        
        if not paths:
            logger.error(f"❌ Aucun fichier trouvé correspondant à '{target_path}'")
            return 1
            
        logger.info(f"✅ {len(paths)} fichier(s) trouvé(s): {', '.join(paths)}")
        
        # Analyser chaque fichier un par un
        for i, path in enumerate(paths):
            logger.info(f"📄 ({i+1}/{len(paths)}) Analyse de {path}...")
            
            # Exécuter l'équipe de revue
            start_time = time.time()
            try:
                review_crew = ReviewCrew(owner=owner, repo=repo, page_id=page_id, path=path)
                result = review_crew.run()
                elapsed_time = time.time() - start_time
                
                # Afficher les résultats
                logger.info(f"✅ Revue terminée pour {path} en {elapsed_time:.2f} secondes")
                logger.info(f"Résultat: {result}")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'analyse de {path}: {e}")
                if logger.level == logging.DEBUG:
                    logger.debug(f"Traceback: {traceback.format_exc()}")
        
        logger.info(f"✅ Toutes les revues sont terminées! ({len(paths)} fichier(s) analysé(s))")
        if page_id:
            logger.info(f"📝 Les résultats ont été exportés vers Notion")
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse: {e}")
        if logger.level == logging.DEBUG:
            logger.debug(f"Traceback: {traceback.format_exc()}")
        return 1
    
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
