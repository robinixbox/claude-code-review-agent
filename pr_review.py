#!/usr/bin/env python
"""
Script d'analyse automatique des pull requests
Permet l'exécution via GitHub Actions lors d'une PR
"""
import os
import argparse
import requests
import json
from claude_code_reviewer import ReviewCrew

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Agent d'analyse automatique des pull requests")
    parser.add_argument("--repo", type=str, required=True, help="Nom du dépôt au format 'owner/repo'")
    parser.add_argument("--pr", type=int, required=True, help="Numéro de la pull request")
    return parser.parse_args()

def get_pr_files(owner, repo, pr_number, github_token):
    """Get the list of files changed in a PR"""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {"Authorization": f"token {github_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des fichiers de la PR: {e}")
        return []

def post_pr_comment(owner, repo, pr_number, comment, github_token):
    """Post a comment on a pull request"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la publication du commentaire: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🤖 AGENT D'ANALYSE DES PULL REQUESTS")
    print("=" * 50)
    
    # Parse command line arguments
    args = parse_args()
    
    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_API_KEY")
    if not github_token:
        print("❌ Token GitHub non trouvé. Configurez la variable d'environnement GITHUB_API_KEY.")
        return
    
    # Split repository into owner and repo
    try:
        owner, repo = args.repo.split('/')
    except ValueError:
        print("❌ Format de dépôt invalide. Utilisez le format 'owner/repo'.")
        return
    
    print(f"\n🔍 Analyse de la PR #{args.pr} dans {args.repo}...")
    
    # Get files changed in the PR
    pr_files = get_pr_files(owner, repo, args.pr, github_token)
    if not pr_files:
        print("❌ Aucun fichier trouvé dans la PR ou erreur lors de la récupération.")
        return
    
    print(f"✅ {len(pr_files)} fichier(s) trouvé(s) dans la PR")
    
    # Create a Notion page if API keys are configured
    page_id = None
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    
    if notion_api_key and notion_page_id:
        try:
            from claude_code_reviewer import create_notion_page
            page_id = create_notion_page(project_name=f"{repo} PR #{args.pr}")
            if page_id:
                print(f"✅ Page Notion créée pour stocker les résultats")
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de la page Notion: {e}")
    
    # Filter files to analyze (only Python files or other relevant files)
    python_files = [file for file in pr_files if file['filename'].endswith('.py') and file['status'] != 'removed']
    
    if not python_files:
        print("❌ Aucun fichier Python trouvé dans la PR.")
        comment = "⚠️ **Revue de code automatique**\n\nAucun fichier Python trouvé dans cette PR. Aucune analyse effectuée."
        post_pr_comment(owner, repo, args.pr, comment, github_token)
        return
    
    print(f"✅ {len(python_files)} fichier(s) Python à analyser")
    
    # Prepare the comment for PR
    review_results = []
    
    # Analyze each file one by one
    for i, file in enumerate(python_files):
        filename = file['filename']
        print(f"\n📄 ({i+1}/{len(python_files)}) Analyse de {filename}...")
        
        # Execute the review crew
        review_crew = ReviewCrew(owner=owner, repo=repo, page_id=page_id, path=filename)
        result = review_crew.run()
        
        # Save the result
        review_results.append({
            "file": filename,
            "result": result
        })
        
        # Display results
        print(f"✅ Revue terminée pour {filename}")
    
    # Format PR comment
    review_comment = "# 🤖 Revue de code automatique\n\n"
    review_comment += f"J'ai analysé {len(python_files)} fichier(s) Python dans cette PR.\n\n"
    
    for result in review_results:
        try:
            # Assuming result is a string representation of a list or tuple
            parsed_result = json.loads(result["result"].replace("'", "\""))
            if len(parsed_result) >= 3:
                file_path = parsed_result[1]
                review_text = parsed_result[2]
                
                review_comment += f"## Fichier: `{file_path}`\n\n"
                review_comment += f"{review_text}\n\n"
                review_comment += "---\n\n"
        except Exception as e:
            review_comment += f"## Fichier: `{result['file']}`\n\n"
            review_comment += "⚠️ Erreur lors de l'analyse de ce fichier.\n\n"
            review_comment += "---\n\n"
    
    review_comment += "\n\n> Cette revue a été générée automatiquement par Claude Code Review Agent."
    
    # Post comment on PR
    if post_pr_comment(owner, repo, args.pr, review_comment, github_token):
        print("✅ Commentaire publié sur la PR avec succès!")
    else:
        print("❌ Échec de la publication du commentaire sur la PR.")
    
    print("\n✅ Analyse de la PR terminée!")
    if page_id:
        print(f"📝 Les résultats ont été exportés vers Notion")

if __name__ == "__main__":
    main()
