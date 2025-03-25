#!/usr/bin/env python
"""
Script d'exécution autonome pour l'agent de revue de code
Permet l'exécution via GitHub Actions ou en ligne de commande
"""
import os
import json
import argparse
import ast
import traceback
import logging
from claude_code_reviewer import ReviewCrew

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Agent de revue de code autonome")
    parser.add_argument("--repo", type=str, help="URL du dépôt GitHub à analyser")
    parser.add_argument("--target", type=str, help="Nom du fichier ou du dossier à examiner")
    parser.add_argument("--config", type=str, help="Chemin vers un fichier de configuration JSON")
    return parser.parse_args()

def load_config(config_path):
    """Load configuration from a JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"✅ Configuration chargée depuis {config_path}")
            return config
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement de la configuration: {e}")
        return None

def main():
    """Main function"""
    print("=" * 50)
    print("🤖 AGENT AUTONOME DE REVUE DE CODE")
    print("=" * 50)
    
    # Parse command line arguments
    args = parse_args()
    
    # Load configuration from file if specified
    config = None
    if args.config:
        config = load_config(args.config)
    
    # Determine repository URL and target path
    repo_url = args.repo if args.repo else (config.get('repo_url') if config else None)
    target_path = args.target if args.target else (config.get('target_path') if config else None)
    
    if not repo_url:
        logger.error("❌ URL du dépôt GitHub non spécifiée. Utilisez --repo ou un fichier de configuration.")
        return
    
    if not target_path:
        logger.error("❌ Chemin cible non spécifié. Utilisez --target ou un fichier de configuration.")
        return
    
    # Extract owner and repository from GitHub URL
    try:
        split_url = repo_url.split('/')
        owner = split_url[3]
        repo = split_url[4]
    except IndexError:
        logger.error("❌ URL GitHub invalide. Format attendu: https://github.com/username/repository")
        return
    
    logger.info(f"🔍 Analyse du dépôt {owner}/{repo}...")
    
    # Retrieve repository file tree
    from claude_code_reviewer import get_file_tree, global_path
    get_file_tree(owner=owner, repo=repo)
    
    if not global_path:
        logger.error("❌ Impossible de récupérer la structure du dépôt. Vérifiez vos identifiants et l'URL.")
        return
    
    logger.info("✅ Structure du dépôt récupérée")
    
    # Create a Notion page if API keys are configured
    page_id = None
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    
    if notion_api_key and notion_page_id:
        try:
            from claude_code_reviewer import create_notion_page
            page_id = create_notion_page(project_name=repo)
            if page_id:
                logger.info(f"✅ Page Notion créée pour stocker les résultats")
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la création de la page Notion: {e}")
    
    # Import the PathAgent to find matching files
    from claude_code_reviewer import Agents, Tasks
    
    path_agent = Agents.path_agent()
    if not path_agent:
        logger.error("❌ Impossible de créer l'agent de chemin. Vérifiez votre clé API Claude.")
        return
        
    path_task = Tasks.get_file_path_task(agent=path_agent, filetree=global_path, user_input=target_path)
    
    logger.info(f"🔍 Recherche des fichiers correspondant à '{target_path}'...")
    
    try:
        paths_output = path_task.execute()
        
        # Tenter d'analyser le résultat comme JSON d'abord
        try:
            paths = json.loads(paths_output)
        except json.JSONDecodeError:
            # Si ce n'est pas un JSON valide, essayer avec ast.literal_eval
            paths = ast.literal_eval(paths_output)
        
        if not paths:
            logger.error(f"❌ Aucun fichier trouvé correspondant à '{target_path}'")
            return
            
        logger.info(f"✅ {len(paths)} fichier(s) trouvé(s)")
        
        # Récupérer la limite de fichiers depuis la configuration
        max_files = 10  # Valeur par défaut
        if config and 'review_settings' in config and 'max_files_per_run' in config['review_settings']:
            max_files = config['review_settings']['max_files_per_run']
        
        # Limiter le nombre de fichiers à analyser
        if len(paths) > max_files:
            logger.warning(f"⚠️ Limitation à {max_files} fichiers sur les {len(paths)} trouvés")
            paths = paths[:max_files]
        
        # Analyze each file one by one
        results = []
        for i, path in enumerate(paths):
            logger.info(f"📄 ({i+1}/{len(paths)}) Analyse de {path}...")
            
            try:
                # Execute the review crew
                review_crew = ReviewCrew(owner=owner, repo=repo, page_id=page_id, path=path)
                result = review_crew.run()
                
                # Enregistrer le résultat
                results.append({
                    "file": path,
                    "result": result,
                    "success": True
                })
                
                # Display results
                logger.info(f"✅ Revue terminée pour {path}")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'analyse de {path}: {e}")
                logger.error(traceback.format_exc())
                results.append({
                    "file": path,
                    "result": str(e),
                    "success": False
                })
        
        # Résumé des résultats
        success_count = sum(1 for r in results if r["success"])
        logger.info(f"\n✅ {success_count}/{len(paths)} revues terminées avec succès!")
        
        if success_count < len(paths):
            logger.warning(f"⚠️ {len(paths) - success_count} fichier(s) n'ont pas pu être analysés")
            
        # Afficher le détail des erreurs
        for result in [r for r in results if not r["success"]]:
            logger.error(f"❌ Échec pour {result['file']}: {result['result']}")
        
        if page_id:
            logger.info(f"📝 Les résultats ont été exportés vers Notion")
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
