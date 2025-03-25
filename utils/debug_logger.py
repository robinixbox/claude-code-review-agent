#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de journalisation avancé pour le débogage de l'agent de revue de code.
Fournit des fonctionnalités de journalisation détaillées avec contexte et traçage.
"""

import os
import sys
import json
import time
import logging
import traceback
from datetime import datetime
from pathlib import Path
from functools import wraps

# Configuration des couleurs pour la console
COLORS = {
    'RESET': '\033[0m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
}

# Création du dossier de logs s'il n'existe pas
logs_dir = Path('./logs')
logs_dir.mkdir(exist_ok=True)

# Configuration du format de journalisation
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Création du fichier de log avec horodatage
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = logs_dir / f"agent_debug_{timestamp}.log"

# Configuration du gestionnaire de journalisation
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

# Création du logger
logger = logging.getLogger("CodeReviewAgent")

def log_api_call(api_name):
    """
    Décorateur pour journaliser les appels API avec leurs paramètres et résultats.
    
    Args:
        api_name: Nom de l'API appelée
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Journalisation du début de l'appel
            arg_str = ', '.join([str(a) for a in args])
            kwarg_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
            params = f"{arg_str}{', ' if arg_str and kwarg_str else ''}{kwarg_str}"
            
            logger.info(f"{COLORS['CYAN']}Calling {api_name} with params: {params}{COLORS['RESET']}")
            
            start_time = time.time()
            try:
                # Exécution de la fonction
                result = func(*args, **kwargs)
                
                # Journalisation du succès
                duration = time.time() - start_time
                if isinstance(result, (dict, list)):
                    # Limiter la taille du résultat pour éviter des logs trop volumineux
                    result_str = json.dumps(result, indent=2)
                    if len(result_str) > 1000:
                        result_str = result_str[:1000] + "... [output truncated]"
                else:
                    result_str = str(result)
                    if len(result_str) > 1000:
                        result_str = result_str[:1000] + "... [output truncated]"
                
                logger.info(f"{COLORS['GREEN']}✓ {api_name} completed in {duration:.2f}s{COLORS['RESET']}")
                logger.debug(f"Result: {result_str}")
                
                return result
            except Exception as e:
                # Journalisation de l'erreur
                duration = time.time() - start_time
                logger.error(f"{COLORS['RED']}✗ {api_name} failed after {duration:.2f}s: {str(e)}{COLORS['RESET']}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
        
        return wrapper
    return decorator

def log_agent_action(action_name):
    """
    Décorateur pour journaliser les actions des agents.
    
    Args:
        action_name: Nom de l'action effectuée par l'agent
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"{COLORS['YELLOW']}▶ Agent action: {action_name}{COLORS['RESET']}")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{COLORS['GREEN']}✓ Agent action '{action_name}' completed in {duration:.2f}s{COLORS['RESET']}")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{COLORS['RED']}✗ Agent action '{action_name}' failed after {duration:.2f}s: {str(e)}{COLORS['RESET']}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
        
        return wrapper
    return decorator

def dump_context(context, label="Context"):
    """
    Journalise un objet contexte pour le débogage.
    
    Args:
        context: L'objet contexte à journaliser
        label: Label pour identifier le contexte
    """
    try:
        if isinstance(context, (dict, list)):
            context_str = json.dumps(context, indent=2)
        else:
            context_str = str(context)
        
        logger.debug(f"{COLORS['PURPLE']}{label}:{COLORS['RESET']}\n{context_str}")
    except Exception as e:
        logger.error(f"Failed to dump context: {str(e)}")

def exception_to_string(exc):
    """
    Convertit une exception en chaîne de caractères détaillée.
    
    Args:
        exc: L'exception à convertir
        
    Returns:
        Chaîne de caractères avec détails de l'exception
    """
    stack = traceback.extract_tb(exc.__traceback__)
    pretty = traceback.format_list(stack)
    return f"{str(exc)}\n\nStack trace:\n{''.join(pretty)}"

def log_step(message):
    """
    Journalise une étape du processus avec un format distinct.
    
    Args:
        message: Message décrivant l'étape
    """
    separator = "=" * 40
    logger.info(f"\n{COLORS['BLUE']}{separator}\n{message}\n{separator}{COLORS['RESET']}")
