#!/usr/bin/env python
"""
Fonctions utilitaires pour l'agent de revue de code
"""
import os
import json
import logging
import requests
import traceback
from typing import Dict, List, Any, Union, Optional, Tuple

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_repo_info(repo_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extrait le propriétaire et le nom du dépôt à partir d'une URL GitHub.
    
    Args:
        repo_url: URL du dépôt GitHub (format: https://github.com/username/repository)
        
    Returns:
        Tuple contenant le propriétaire et le nom du dépôt, ou (None, None) en cas d'erreur
    """
    try:
        split_url = repo_url.split('/')
        owner = split_url[3]
        repo = split_url[4].split('.')[0]  # Gère aussi les URLs qui finissent par .git
        return owner, repo
    except (IndexError, AttributeError) as e:
        logger.error(f"❌ URL GitHub invalide: {e}")
        logger.error("Format attendu: https://github.com/username/repository")
        return None, None

def get_pr_files(owner: str, repo: str, pr_number: int, github_token: str) -> List[Dict[str, Any]]:
    """
    Récupère la liste des fichiers modifiés dans une PR.
    
    Args:
        owner: Propriétaire du dépôt
        repo: Nom du dépôt
        pr_number: Numéro de la pull request
        github_token: Token d'API GitHub
        
    Returns:
        Liste des fichiers modifiés
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = {"Authorization": f"token {github_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur HTTP lors de la récupération des fichiers de la PR: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des fichiers de la PR: {e}")
        logger.error(traceback.format_exc())
        return []

def post_pr_comment(owner: str, repo: str, pr_number: int, comment: str, github_token: str) -> bool:
    """
    Publie un commentaire sur une pull request.
    
    Args:
        owner: Propriétaire du dépôt
        repo: Nom du dépôt
        pr_number: Numéro de la pull request
        comment: Contenu du commentaire
        github_token: Token d'API GitHub
        
    Returns:
        True si le commentaire a été publié avec succès, False sinon
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"✅ Commentaire publié avec succès sur la PR #{pr_number}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur HTTP lors de la publication du commentaire: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lors de la publication du commentaire: {e}")
        logger.error(traceback.format_exc())
        return False

def filter_python_files(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtre une liste de fichiers pour ne garder que les fichiers Python non supprimés.
    
    Args:
        files: Liste de fichiers retournée par l'API GitHub
        
    Returns:
        Liste filtrée de fichiers Python
    """
    return [file for file in files if file['filename'].endswith('.py') and file['status'] != 'removed']

def safe_parse_json(json_str: str) -> Any:
    """
    Tente de parser une chaîne JSON en appliquant différentes stratégies.
    
    Args:
        json_str: Chaîne JSON à parser
        
    Returns:
        Objet Python correspondant au JSON, ou la chaîne originale en cas d'échec
    """
    if not isinstance(json_str, str):
        return json_str
        
    try:
        # Essayer d'abord en supposant que c'est un JSON valide
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            # Si ce n'est pas un JSON valide, essayer en remplaçant les apostrophes
            return json.loads(json_str.replace("'", "\""))
        except json.JSONDecodeError:
            # Retourner la chaîne originale si toutes les tentatives échouent
            return json_str
