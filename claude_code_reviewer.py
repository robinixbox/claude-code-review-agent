#!/usr/bin/env python
"""
Agent de revue de code autonome utilisant CrewAI et Claude API
"""
import os
import ast
import base64
import json
import requests
from dotenv import load_dotenv
from textwrap import dedent
from langchain.tools import tool
from crewai import Agent, Task, Crew, Process
from anthropic import Anthropic

# Chargement des variables d'environnement
load_dotenv()

# Configuration des clés API
# Vous pouvez remplacer les clés ci-dessous par vos propres clés ou les mettre dans un fichier .env
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "sk-ant-api03-...")  # Remplacez par votre clé
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY", "ghp_CohWQti...")  # Remplacez par votre clé
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "robinixbox")  # Remplacez par votre nom d'utilisateur

# Configuration d'Anthropic (Claude API)
print("🔌 Initialisation de l'API Claude...")
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Variable globale pour stocker la structure du dépôt
global_path = ""

# Configuration Notion (si la clé est présente)
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
if NOTION_API_KEY:
    from notion_client import Client
    notion = Client(auth=NOTION_API_KEY)
    print("✅ API Notion configurée")

def create_notion_page(project_name):
    """
    Crée une page Notion pour stocker les résultats de la revue
    """
    if not NOTION_API_KEY or not NOTION_PAGE_ID:
        print("⚠️ Configuration Notion incomplète. Les résultats ne seront pas exportés.")
        return None
        
    parent = {"type": "page_id", "page_id": NOTION_PAGE_ID}
    properties = {
        "title": {
            "type": "title",
            "title": [{"type": "text", "text": {"content": f"Code review de {project_name}"}}]
        },
    }
    
    try:
        create_page_response = notion.pages.create(parent=parent, properties=properties)
        return create_page_response['id']
    except Exception as e:
        print(f"❌ Erreur lors de la création de la page Notion: {e}")
        return None

def get_file_tree(owner, repo, path='', level=0):
    """
    Récupère et affiche la structure arborescente d'un dépôt GitHub, en ignorant 
    certains dossiers spécifiques.
    
    Paramètres:
    - owner: Le nom d'utilisateur du propriétaire du dépôt.
    - repo: Le nom du dépôt.
    - path: Le chemin à récupérer. Laisser vide pour récupérer le répertoire racine.
    - level: La profondeur actuelle dans la structure arborescente.
    """
    # Répertoires à ignorer
    ignore_dirs = {'public', 'images', 'media', 'assets', 'node_modules', '.git'}
    global global_path
    
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    # Ajout de l'en-tête Authorization avec le token
    headers = {'Authorization': f'token {GITHUB_API_KEY}'}
    
    try:
        # Effectue la requête
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code}: {response.reason}")
            print(f"URL: {api_url}")
            return
            
        items = response.json()
        
        if isinstance(items, list):
            for item in items:
                # Ignorer les répertoires spécifiés
                if item['name'] in ignore_dirs:
                    continue
                
                global_path += f"{' ' * (level * 2)}- {item['name']}\n"
                if item['type'] == 'dir':
                    get_file_tree(owner, repo, item['path'], level + 1)
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la structure du dépôt: {e}")

class Tools:
    """Outils personnalisés pour les agents"""
    
    @tool("Add data to notion")
    def add_to_notion(output, page_id):
        """
        Utilisé pour ajouter des données à un document Notion.
        """
        if not NOTION_API_KEY or not page_id:
            return "Notion n'est pas configuré. Les résultats ne seront pas exportés."
        
        try:
            children = [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "🚀 Nom du fichier"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": output[1]}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "📝 Revue"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": output[2]}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "💡 Code amélioré"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "caption": [],
                        "rich_text": [{
                            "type": "text",
                            "text": {
                                "content": output[3]
                            }
                        }],
                        "language": "python"  # À adapter en fonction du type de fichier
                    }
                },
            ]
            
            add_data_response = notion.blocks.children.append(
                block_id=page_id, children=children
            )
            return "Données ajoutées avec succès à Notion"
        except Exception as e:
            return f"Erreur lors de l'ajout à Notion: {e}"

    @tool("get file contents from given file path")
    def get_file_contents(path, owner, repo):
        """
        Utilisé pour obtenir le contenu d'un fichier à partir du chemin, du propriétaire 
        du dépôt et du nom du dépôt.
        L'URL ressemblera à https://api.github.com/repos/{owner}/{repo}/{path}
        """
        if path.startswith("https://"):
            api_url = path
        else:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        
        # Ajout de l'en-tête Authorization avec le token
        headers = {'Authorization': f'token {GITHUB_API_KEY}', 'X-GitHub-Api-Version': '2022-11-28'}
        
        try:
            # Effectue la requête
            response = requests.get(api_url, headers=headers)
            
            # Vérifie si la requête a réussi
            if response.status_code == 200:
                file_content = response.json()
                
                # Vérifie la taille du fichier
                if file_content['size'] > 1000000:  # 1MB en octets
                    return "Ignoré: Taille du fichier supérieure à 1 Mo."
                
                # Le contenu est encodé en Base64, donc on le décode
                content_decoded = base64.b64decode(file_content['content'])
                
                # Convertit les octets en chaîne de caractères
                content_str = content_decoded.decode('utf-8')
                
                # Vérifie le nombre de lignes dans le fichier
                if len(content_str.split('\n')) > 1000:
                    return "Ignoré: Le fichier contient plus de 1000 lignes."
                    
                return content_str
            else:
                # Gère les erreurs (par exemple, fichier non trouvé, accès refusé)
                return f"Erreur: {response.status_code} - {response.reason}"
        except Exception as e:
            return f"Erreur lors de la récupération du contenu: {e}"

class Tasks:
    """Définition des tâches pour les agents"""
    
    def review_task(agent, repo, context):
        """Tâche de revue de code"""
        return Task(
            agent=agent,
            description=dedent(
                f"""
                Examine le fichier donné et fournis des retours détaillés sur les points qui ne respectent pas 
                les standards de code de l'industrie.
                Prends le chemin du fichier et son contenu depuis l'agent contentAgent.
                Apporte des modifications au contenu du fichier pour l'améliorer et renvoie le contenu modifié 
                comme updated_code dans la réponse.
                
                Renvoie les valeurs suivantes dans la réponse :
                project_name: {repo}
                file_path: chemin_du_fichier
                review: revue_ici
                updated_code: contenu mis à jour du fichier après modifications
                
                Renvoie la sortie qui suit la structure de tableau ci-dessous, chaque élément devant être 
                enveloppé dans une chaîne multilignes.
                Dans le cas d'updated_code, ajoute le code complet sous forme de chaîne multiligne.
                Renvoie uniquement le contenu du fichier qui a été modifié dans updated_code ; s'il y a 
                plusieurs modifications dans le contenu du fichier, alors envoie tout le contenu du fichier.
                
                Chaque tableau doit suivre ce format :
                [project_name, file_path, review, updated_code]
                
                Ne renvoie rien d'autre que le tableau au format ci-dessus.
                """),
            context=context,
            expected_output="Un tableau de 4 éléments au format donné dans la description"
        )
        
    def notion_task(agent, context, page_id):
        """Tâche d'ajout à Notion"""
        return Task(
            agent=agent,
            description=dedent(f"""
            On te donne un tableau de 4 éléments et un ID de page, et tu dois ajouter ces données dans Notion.
            Voici l'ID de la page Notion :
            {page_id}
            Dis 'Données ajoutées avec succès à Notion' en cas de succès, sinon renvoie le tableau donné.
            """),
            context=context,
            expected_output="Texte indiquant 'Données ajoutées avec succès à Notion' en cas de succès et 'Impossible d'ajouter des données à Notion' en cas d'échec"
        )
        
    def get_file_path_task(agent, filetree, user_input):
        """Tâche de récupération des chemins de fichiers"""
        return Task(
            agent=agent,
            description=dedent(f"""
            On te donne une structure arborescente de dossier et une entrée utilisateur, et tu dois d'abord déterminer 
            s'il s'agit d'un dossier ou d'un fichier à partir de la structure arborescente donnée.
            
            Suis cette approche :
            - S'il s'agit d'un fichier, renvoie un tableau avec 1 élément qui contient le chemin complet de ce fichier 
              dans cette structure de dossier
            - S'il s'agit d'un dossier, renvoie un tableau de chemins des sous-fichiers dans ce dossier ; s'il y a un 
              sous-dossier dans le dossier donné, renvoie également les chemins pour ces fichiers
            - Si l'entrée utilisateur n'est pas présente dans la structure arborescente donnée, renvoie simplement un 
              tableau vide
              
            Renvoie le chemin COMPLET d'un fichier donné dans la structure de dossier donnée.
            Par exemple, si la structure arborescente ressemble à ceci :
            - src
              - components
                - Login.jsx
                - Password.jsx
            - backend
              - api
              
            Alors le chemin complet de Login.jsx sera src/components/Login.jsx
            
            N'ENVOIE PAS tout le contenu du fichier en une seule fois, envoie-le un par un à reviewAgent.
            
            Voici la structure arborescente du dossier :
            {filetree}
            
            Voici l'entrée utilisateur :
            {user_input}
            
            REMARQUE : RENVOIE UNIQUEMENT UN TABLEAU DE CHEMINS SANS TEXTE SUPPLÉMENTAIRE DANS LA RÉPONSE
            """),
            expected_output=dedent("""
            UNIQUEMENT un tableau de chemins
            Par exemple :
            ['src/load/app.jsx', 'client/app/pages/404.js']
            """)
        )
        
    def get_file_content_task(agent, owner, repo, path):
        """Tâche de récupération du contenu d'un fichier"""
        return Task(
            agent=agent,
            description=dedent(f"""
            On te donne un chemin de fichier et tu dois obtenir le contenu du fichier et le nom du fichier 
            en utilisant l'API GitHub.
            
            Voici le chemin du fichier :
            {path}
            
            Voici le nom du propriétaire :
            {owner}
            
            Voici le nom du dépôt :
            {repo}
            
            Ne renvoie rien d'autre que le nom du fichier et le contenu.
            """),
            expected_output="Nom de fichier et contenu du fichier donné"
        )

class Agents:
    """Définition des agents"""
    
    def review_agent():
        """Agent de revue de code"""
        return Agent(
            role='Senior software developer',
            goal="Effectuer des revues de code sur un fichier donné pour vérifier s'il correspond aux standards de code de l'industrie",
            backstory="Tu es un développeur logiciel senior dans une grande entreprise et tu dois effectuer une revue de code sur un contenu de fichier donné.",
            allow_delegation=False,
            verbose=True,
            # Utilisation de Claude API
            llm_config={
                "provider": anthropic_client,
                "model": "claude-3-opus-20240229",
                "temperature": 0.2
            }
        )
        
    def notion_agent():
        """Agent Notion"""
        return Agent(
            role="Expert API Notion et rédacteur de contenu",
            goal="Ajouter les données du tableau donné dans le document Notion en utilisant l'outil addToNotion",
            backstory="Tu es un expert de l'API Notion qui peut utiliser l'outil addToNotion et ajouter les données fournies dans un document Notion",
            allow_delegation=True,
            tools=[Tools.add_to_notion],
            verbose=True,
            # Utilisation de Claude API
            llm_config={
                "provider": anthropic_client,
                "model": "claude-3-haiku-20240307",
                "temperature": 0.1
            }
        )
        
    def path_agent():
        """Agent de chemin de fichier"""
        return Agent(
            role="Extracteur de chemin de fichier",
            goal="Obtenir la structure arborescente du dossier et renvoyer les chemins complets du fichier donné ou des fichiers du dossier donné au format tableau",
            backstory="Tu es un extracteur de chemin de fichier qui a créé plusieurs chemins de fichiers à partir de la structure arborescente donnée",
            allow_delegation=False,
            verbose=True,
            # Utilisation de Claude API
            llm_config={
                "provider": anthropic_client,
                "model": "claude-3-haiku-20240307",
                "temperature": 0.1
            }
        )
        
    def content_agent():
        """Agent de contenu"""
        return Agent(
            role="Expert API GitHub",
            goal="Obtenir le contenu du fichier donné en utilisant l'API GitHub",
            backstory="Tu es un expert de l'API GitHub qui a extrait de nombreux contenus de fichiers en utilisant l'API de GitHub",
            verbose=True,
            allow_delegation=False,
            tools=[Tools.get_file_contents],
            # Utilisation de Claude API
            llm_config={
                "provider": anthropic_client,
                "model": "claude-3-haiku-20240307",
                "temperature": 0.1
            }
        )

class ReviewCrew:
    """Équipe de revue de code"""
    
    def __init__(self, owner, repo, page_id, path):
        """Initialisation de l'équipe"""
        self.owner = owner
        self.repo = repo
        self.page_id = page_id
        self.path = path
        
    def run(self):
        """Exécution de l'équipe"""
        # Agents
        review_agent = Agents.review_agent()
        content_agent = Agents.content_agent()
        notion_agent = Agents.notion_agent() if NOTION_API_KEY else None
        
        # Tâches
        content_task = Tasks.get_file_content_task(
            agent=content_agent, 
            owner=self.owner, 
            repo=self.repo, 
            path=self.path
        )
        
        review_task = Tasks.review_task(
            agent=review_agent, 
            repo=self.repo, 
            context=[content_task]
        )
        
        agents = [content_agent, review_agent]
        tasks = [content_task, review_task]
        
        # Ajouter la tâche Notion si configurée
        if notion_agent and self.page_id:
            notion_task = Tasks.notion_task(
                agent=notion_agent, 
                page_id=self.page_id, 
                context=[review_task]
            )
            tasks.append(notion_task)
            agents.append(notion_agent)
        
        # Équipe
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=2,  # Tu peux le définir à 1 ou 2 pour différents niveaux de journalisation
            process=Process.sequential
        )
        
        # Exécution de l'équipe
        result = crew.kickoff()
        return result

def main():
    """Fonction principale"""
    print("=" * 50)
    print("📝 AGENT DE REVUE DE CODE AVEC CLAUDE & CREWAI")
    print("=" * 50)
    
    # Vérification des clés API
    if not ANTHROPIC_API_KEY:
        print("❌ Clé API Anthropic (Claude) non trouvée. Veuillez configurer la variable d'environnement ANTHROPIC_API_KEY.")
        return
    
    if not GITHUB_API_KEY:
        print("❌ Clé API GitHub non trouvée. Veuillez configurer la variable d'environnement GITHUB_API_KEY.")
        return
    
    # Saisie utilisateur
    github_url = input("URL du dépôt GitHub à analyser (ex: https://github.com/username/repository): ")
    user_input = input("Nom du fichier ou du dossier à examiner: ")
    
    # Extraction du propriétaire et du dépôt à partir de l'URL GitHub
    try:
        split_url = github_url.split('/')
        owner = split_url[3]
        repo = split_url[4]
    except IndexError:
        print("❌ URL GitHub invalide. Format attendu: https://github.com/username/repository")
        return
    
    print(f"\n🔍 Analyse du dépôt {owner}/{repo}...")
    
    # Récupération de la structure arborescente du dépôt GitHub
    global global_path
    global_path = ""
    get_file_tree(owner=owner, repo=repo)
    
    if not global_path:
        print("❌ Impossible de récupérer la structure du dépôt. Vérifiez vos identifiants et l'URL.")
        return
    
    print(f"✅ Structure du dépôt récupérée")
    
    # Création d'une page Notion si les clés sont configurées
    page_id = None
    if NOTION_API_KEY and NOTION_PAGE_ID:
        try:
            page_id = create_notion_page(project_name=repo)
            if page_id:
                print(f"✅ Page Notion créée pour stocker les résultats")
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de la page Notion: {e}")
    
    # Récupération des chemins de fichiers à partir de l'entrée utilisateur
    path_agent = Agents.path_agent()
    path_task = Tasks.get_file_path_task(agent=path_agent, filetree=global_path, user_input=user_input)
    
    print(f"\n🔍 Recherche des fichiers correspondant à '{user_input}'...")
    paths_output = path_task.execute()
    
    try:
        paths = ast.literal_eval(paths_output)
        
        if not paths:
            print(f"❌ Aucun fichier trouvé correspondant à '{user_input}'")
            return
            
        print(f"✅ {len(paths)} fichier(s) trouvé(s)")
        
        # Analyse de chaque fichier un par un
        for i, path in enumerate(paths):
            print(f"\n📄 ({i+1}/{len(paths)}) Analyse de {path}...")
            
            # Exécution de l'équipe de revue
            review_crew = ReviewCrew(owner=owner, repo=repo, page_id=page_id, path=path)
            result = review_crew.run()
            
            # Affichage des résultats
            print(f"✅ Revue terminée pour {path}")
            print(f"Résultat: {result}")
        
        print("\n✅ Toutes les revues sont terminées!")
        if page_id:
            print(f"📝 Les résultats ont été exportés vers Notion")
    
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")

if __name__ == "__main__":
    main()
