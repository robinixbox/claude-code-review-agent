#!/usr/bin/env python
"""
Script d'exécution autonome pour l'agent de revue de code
Permet l'exécution via GitHub Actions ou en ligne de commande
"""
import os
import json
import argparse
import ast
from claude_code_reviewer import ReviewCrew

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
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erreur lors du chargement de la configuration: {e}")
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
        print("❌ URL du dépôt GitHub non spécifiée. Utilisez --repo ou un fichier de configuration.")
        return
    
    if not target_path:
        print("❌ Chemin cible non spécifié. Utilisez --target ou un fichier de configuration.")
        return
    
    # Extract owner and repository from GitHub URL
    try:
        split_url = repo_url.split('/')
        owner = split_url[3]
        repo = split_url[4]
    except IndexError:
        print("❌ URL GitHub invalide. Format attendu: https://github.com/username/repository")
        return
    
    print(f"\n🔍 Analyse du dépôt {owner}/{repo}...")
    
    # Retrieve repository file tree
    from claude_code_reviewer import get_file_tree, global_path
    get_file_tree(owner=owner, repo=repo)
    
    if not global_path:
        print("❌ Impossible de récupérer la structure du dépôt. Vérifiez vos identifiants et l'URL.")
        return
    
    print(f"✅ Structure du dépôt récupérée")
    
    # Create a Notion page if API keys are configured
    page_id = None
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    
    if notion_api_key and notion_page_id:
        try:
            from claude_code_reviewer import create_notion_page
            page_id = create_notion_page(project_name=repo)
            if page_id:
                print(f"✅ Page Notion créée pour stocker les résultats")
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de la page Notion: {e}")
    
    # Import the PathAgent to find matching files
    from claude_code_reviewer import Agents, Tasks
    
    path_agent = Agents.path_agent()
    path_task = Tasks.get_file_path_task(agent=path_agent, filetree=global_path, user_input=target_path)
    
    print(f"\n🔍 Recherche des fichiers correspondant à '{target_path}'...")
    paths_output = path_task.execute()
    
    try:
        paths = ast.literal_eval(paths_output)
        
        if not paths:
            print(f"❌ Aucun fichier trouvé correspondant à '{target_path}'")
            return
            
        print(f"✅ {len(paths)} fichier(s) trouvé(s)")
        
        # Analyze each file one by one
        for i, path in enumerate(paths):
            print(f"\n📄 ({i+1}/{len(paths)}) Analyse de {path}...")
            
            # Execute the review crew
            review_crew = ReviewCrew(owner=owner, repo=repo, page_id=page_id, path=path)
            result = review_crew.run()
            
            # Display results
            print(f"✅ Revue terminée pour {path}")
            print(f"Résultat: {result}")
        
        print("\n✅ Toutes les revues sont terminées!")
        if page_id:
            print(f"📝 Les résultats ont été exportés vers Notion")
    
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")

if __name__ == "__main__":
    main()
