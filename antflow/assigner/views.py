from django.http import JsonResponse
from datetime import datetime, timedelta
import json
import os
import xmlrpc.client

def calculate_end_date(projet, date_debut):
    # Calculer le total des durées des tâches
    total_duree = sum(tache['duree'] for tache in projet['taches'])

    # Initialiser la date de fin estimée
    date_fin = date_debut
    heures_restantes = total_duree

    while heures_restantes > 0:
        # Vérifier si c'est un week-end
        if date_fin.weekday() < 5:  # 0-4 correspond à lundi-vendredi
            # Ajouter 1 jour de travail
            if heures_restantes >= 7:
                heures_restantes -= 7
            else:
                heures_restantes = 0  # Tâches terminées
        # Passer au jour suivant
        date_fin += timedelta(days=1)

    return date_fin

def load_project_json(file_name):
    # Remplace 'chemin/vers/ton/dossier/json' par le chemin vers ton dossier contenant les fichiers JSON
    file_path = os.path.join('type_de_projet/', file_name)
    with open(file_path, 'r') as f:
        return json.load(f)  # Charger et renvoyer le JSON sous forme de dictionnaire

def assign_tasks(request, project_id, start_date):
    # Charger le JSON du projet à partir du fichier
    json_projet = load_project_json(f"{project_id}.json")

    # Convertir start_date en objet datetime
    date_debut = datetime.strptime(start_date, '%Y-%m-%d').date()

    # Calculer la date de fin
    date_fin = calculate_end_date(json_projet, date_debut)

    # Logique d'assignation (exemple basique)
    assignments = []
    for tache in json_projet['taches']:
        # Assignation simple: on prend le premier ID utilisateur assignable pour chaque tâche
        if tache['id_utilisateur_assignable']:
            assigned_user_id = tache['id_utilisateur_assignable'][0]  # Exemple: assigner le premier utilisateur
            assignments.append({
                'id_tache': tache['id'],
                'assigned_user_id': assigned_user_id,
                'date_debut': date_debut.strftime('%Y-%m-%d'),
                'date_fin': date_fin.strftime('%Y-%m-%d')
            })

    return JsonResponse({
        'date_fin': date_fin.strftime('%Y-%m-%d'),
        'assignments': assignments
    })

def connect_and_get_workloads(email, password, start_date, end_date):
    # Configuration de la connexion à Odoo
    url = 'http://localhost:8070'  # Remplace par l'URL de ton instance Odoo
    db = 'Odoo13'                   # Remplace par le nom de ta base de données

    # Connexion à Odoo via XML-RPC
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, email, password, {})
    if not uid:
        print("Échec de connexion")
        return []

    # Accéder à l'API de modèle
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Exemple de recherche des charges de travail
    workloads = models.execute_kw(db, uid, password,
        'user.workload', 'search_read',
        [[('date', '>=', start_date), ('date', '<=', end_date)]],
        {'fields': ['user_id', 'workload_hours']})

    return workloads
