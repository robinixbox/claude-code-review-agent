#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour l'agent de revue de code.
Utilise le journalisation avancée et une configuration ciblée.
"""

import os
import sys
import json
import argparse
import traceback
from pathlib import Path
from datetime import datetime

# Importation des modules de l'agent
from utils.debug_logger import (
    logger, log_step, dump_context, 
    log_api_call, log_agent_action,
    exception_to_string
)
from claude_code_reviewer import (
    ReviewCrew, get_file_tree, global_path,
    Agents, Tasks, create_notion_page
)

@log_api_call("load_config")
def load_config(config_path):
    """
    Charge la configuration depuis un fichier JSON.
    
    Args:
        config_path: Chemin vers le fichier JSON
        
    Returns:
        Dict: Configuration chargée ou None en cas d'erreur
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration chargée depuis {config_path}")
        return config
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")
        return None

@log_agent_action("run_test")
def run_test(config_path="test_config.json"):
    """
    Exécute un test complet de l'agent de revue de code.
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        bool: True si le test a réussi, False sinon
    """
    log_step("DÉMARRAGE DU TEST DE L'AGENT DE REVUE DE CODE")
    logger.info(f"Utilisation du fichier de configuration: {config_path}")

    # Chargement de la configuration
    config = load_config(config_path)
    if not config:
        logger.error("Impossible de charger la configuration")
        return False
        
    dump_context(config, "Configuration")
    
    # Extraction des paramètres
    repo_url = config.get('repo_url')
    target_path = config.get('target_path')
    
    if not repo_url:
        logger.error("URL du dépôt GitHub non spécifiée dans la configuration")
        return False
    
    if not target_path:
        logger.error("Chemin cible non spécifié dans la configuration")
        return False
    
    # Extraction du propriétaire et du dépôt à partir de l'URL GitHub
    try:
        split_url = repo_url.split('/')
        owner = split_url[3]
        repo = split_url[4]
        logger.info(f"Analyse du dépôt {owner}/{repo}")
    except IndexError:
        logger.error(f"URL GitHub invalide: {repo_url}")
        logger.error("Format attendu: https://github.com/username/repository")
        return False
    
    # Récupération de la structure arborescente du dépôt GitHub
    log_step(f"RÉCUPÉRATION DE LA STRUCTURE DU DÉPÔT {owner}/{repo}")
    global global_path
    global_path = ""
    
    try:
        get_file_tree(owner=owner, repo=repo)
        
        if not global_path:
            logger.error("Impossible de récupérer la structure du dépôt")
            logger.error("Vérifiez vos identifiants et l'URL")
            return False
        
        logger.info("Structure du dépôt récupérée avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la structure du dépôt: {e}")
        logger.error(exception_to_string(e))
        return False
    
    # Création d'une page Notion si les clés sont configurées
    page_id = None
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    
    if notion_api_key and notion_page_id:
        log_step("CRÉATION D'UNE PAGE NOTION")
        try:
            page_id = create_notion_page(project_name=repo)
            if page_id:
                logger.info(f"Page Notion créée avec ID: {page_id}")
            else:
                logger.warning("Page Notion non créée")
        except Exception as e:
            logger.error(f"Erreur lors de la création de la page Notion: {e}")
            logger.error(exception_to_string(e))
    else:
        logger.info("API Notion non configurée, les résultats ne seront pas exportés")
    
    # Récupération des chemins de fichiers à partir de l'entrée utilisateur
    log_step(f"RECHERCHE DES FICHIERS: {target_path}")
    
    try:
        path_agent = Agents.path_agent()
        path_task = Tasks.get_file_path_task(
            agent=path_agent, 
            filetree=global_path, 
            user_input=target_path
        )
        
        logger.info(f"Recherche des fichiers correspondant à '{target_path}'...")
        paths_output = path_task.execute()
        
        import ast
        paths = ast.literal_eval(paths_output)
        
        if not paths:
            logger.error(f"Aucun fichier trouvé correspondant à '{target_path}'")
            return False
            
        logger.info(f"{len(paths)} fichier(s) trouvé(s)")
        dump_context(paths, "Chemins trouvés")
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche des fichiers: {e}")
        logger.error(exception_to_string(e))
        return False
    
    # Analyse de chaque fichier un par un
    for i, path in enumerate(paths):
        log_step(f"ANALYSE DU FICHIER ({i+1}/{len(paths)}): {path}")
        
        try:
            # Exécution de l'équipe de revue
            review_crew = ReviewCrew(owner=owner, repo=repo, page_id=page_id, path=path)
            result = review_crew.run()
            
            # Affichage des résultats
            logger.info(f"Revue terminée pour {path}")
            dump_context(result, "Résultat de la revue")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du fichier {path}: {e}")
            logger.error(exception_to_string(e))
            # On continue avec les fichiers suivants
            continue
    
    log_step("FIN DU TEST")
    if page_id:
        logger.info(f"Les résultats ont été exportés vers Notion")
    
    return True

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Test de l'agent de revue de code")
    parser.add_argument("--config", type=str, default="test_config.json", 
                      help="Chemin vers le fichier de configuration JSON")
    args = parser.parse_args()
    
    try:
        success = run_test(config_path=args.config)
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Erreur non gérée: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
