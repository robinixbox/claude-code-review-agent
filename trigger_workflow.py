#!/usr/bin/env python
"""
Script pour déclencher le workflow GitHub Actions de revue de code.
Ce script utilise l'API GitHub pour déclencher manuellement le workflow
sans avoir besoin d'utiliser l'interface web de GitHub.
"""
import os
import sys
import json
import argparse
import requests
import time
from datetime import datetime

def parse_args():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description="Déclencheur de workflow GitHub Actions")
    parser.add_argument("--workflow", type=str, default="code-review-enhanced.yml", 
                       help="Nom du fichier de workflow à déclencher (défaut: code-review-enhanced.yml)")
    parser.add_argument("--repo", type=str, default="robinixbox/claude-code-review-agent", 
                       help="Dépôt au format owner/repo (défaut: robinixbox/claude-code-review-agent)")
    parser.add_argument("--repo-url", type=str, default="https://github.com/robinixbox/claude-code-review-agent", 
                       help="URL du dépôt à analyser (défaut: https://github.com/robinixbox/claude-code-review-agent)")
    parser.add_argument("--target", type=str, default="auto_review_enhanced.py", 
                       help="Fichier ou dossier à analyser (défaut: auto_review_enhanced.py)")
    parser.add_argument("--debug", action="store_true", help="Activer le mode débogage")
    parser.add_argument("--wait", action="store_true", help="Attendre et afficher l'état du workflow")
    parser.add_argument("--token", type=str, help="Token GitHub (par défaut: utilise GITHUB_API_KEY de l'environnement)")
    return parser.parse_args()

def trigger_workflow(owner, repo, workflow_id, inputs, token):
    """Déclenche un workflow GitHub Actions via l'API"""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    data = {
        "ref": "main",  # Branche sur laquelle déclencher le workflow
        "inputs": inputs
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du déclenchement du workflow: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Code de statut: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"Détails de l'erreur: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Réponse: {e.response.text}")
        return False

def get_workflow_runs(owner, repo, workflow_id, token, per_page=10):
    """Récupère les dernières exécutions d'un workflow"""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs?per_page={per_page}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des exécutions du workflow: {e}")
        return None

def monitor_workflow_run(owner, repo, run_id, token, interval=10, max_attempts=30):
    """Surveille l'état d'une exécution de workflow"""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    attempts = 0
    while attempts < max_attempts:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            run_data = response.json()
            
            status = run_data.get('status')
            conclusion = run_data.get('conclusion')
            
            print(f"État: {status}, Conclusion: {conclusion or 'En cours'}")
            
            if status == 'completed':
                run_url = run_data.get('html_url')
                print(f"URL de l'exécution: {run_url}")
                return conclusion == 'success'
            
            time.sleep(interval)
            attempts += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur lors de la surveillance du workflow: {e}")
            return False
    
    print("⚠️ Délai d'attente dépassé pour l'exécution du workflow")
    return False

def main():
    """Fonction principale"""
    # Parse les arguments
    args = parse_args()
    
    # En-tête
    print("=" * 50)
    print("🚀 DÉCLENCHEUR DE WORKFLOW GITHUB ACTIONS")
    print("=" * 50)
    
    # Récupérer le token GitHub
    token = args.token or os.getenv("GITHUB_API_KEY")
    if not token:
        print("❌ Token GitHub non spécifié. Utilisez --token ou définissez GITHUB_API_KEY dans l'environnement.")
        return 1
    
    # Extraire propriétaire et dépôt
    try:
        owner, repo = args.repo.split('/')
    except ValueError:
        print("❌ Format de dépôt invalide. Utilisez le format 'owner/repo'.")
        return 1
    
    # Préparer les inputs pour le workflow
    inputs = {
        "repo_url": args.repo_url,
        "target_path": args.target,
        "debug_mode": str(args.debug).lower()
    }
    
    print(f"📋 Déclenchement du workflow {args.workflow} sur {args.repo}")
    print(f"   - URL du dépôt: {args.repo_url}")
    print(f"   - Cible: {args.target}")
    print(f"   - Mode débogage: {'activé' if args.debug else 'désactivé'}")
    
    # Déclencher le workflow
    if not trigger_workflow(owner, repo, args.workflow, inputs, token):
        return 1
    
    print("✅ Workflow déclenché avec succès!")
    
    # Surveillancer l'exécution du workflow si demandé
    if args.wait:
        print("\n⏳ Surveillance de l'exécution du workflow...")
        time.sleep(5)  # Attendre que le workflow démarre
        
        # Récupérer la dernière exécution du workflow
        runs_data = get_workflow_runs(owner, repo, args.workflow, token, per_page=5)
        if not runs_data or 'workflow_runs' not in runs_data or not runs_data['workflow_runs']:
            print("❌ Impossible de récupérer les exécutions du workflow.")
            return 1
        
        # Trouver la dernière exécution déclenchée manuellement
        for run in runs_data['workflow_runs']:
            if run['event'] == 'workflow_dispatch':
                run_id = run['id']
                print(f"🔍 Surveillance de l'exécution #{run_id}...")
                if monitor_workflow_run(owner, repo, run_id, token):
                    print("✅ Workflow terminé avec succès!")
                else:
                    print("❌ Workflow terminé avec des erreurs ou annulé.")
                break
        else:
            print("⚠️ Aucune exécution récente du workflow trouvée.")
    
    return 0

if __name__ == "__main__":
    # Capture l'heure de début pour calculer le temps total d'exécution
    start_time = time.time()
    
    # Exécution de la fonction principale
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
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
