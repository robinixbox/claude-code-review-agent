
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour l'automatisation des actions GitHub.
Ce fichier a été créé par Claude pour tester le déclenchement 
des workflows GitHub Actions via l'API.
"""

import os
import sys
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Fonction principale du script de test."""
    logger.info("Test d'automatisation démarré à %s", datetime.now().isoformat())
    
    # Afficher des informations sur l'environnement
    logger.info("Version Python: %s", sys.version)
    logger.info("Répertoire de travail: %s", os.getcwd())
    
    logger.info("Test d'automatisation terminé")
    return 0

if __name__ == "__main__":
    sys.exit(main())
