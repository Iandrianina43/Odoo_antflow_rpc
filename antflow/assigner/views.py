# antflow/assigner/views.py

from django.http import JsonResponse
from datetime import datetime, timedelta
import json
import os
import xmlrpc.client

# Fonction pour calculer la date de fin du projet en fonction de la durée des tâches
def calculate_end_date(projet, date_debut):
    # Calculer le total des durées des tâches
    total_duree = sum(tache['duree'] for tache in projet['taches'])
    date_fin = date_debut
    heures_restantes = total_duree

    while heures_restantes > 0:
        if date_fin.weekday() < 5:  # 0-4 correspond à lundi-vendredi
            if heures_restantes >= 7:
                heures_restantes -= 7
            else:
                heures_restantes = 0
        date_fin += timedelta(days=1)
    
    return date_fin

# Fonction pour charger le projet depuis un fichier JSON
def load_project_json(file_name):
    file_path = os.path.join('type_de_projet/', file_name)
    with open(file_path, 'r') as f:
        return json.load(f)

# Fonction pour obtenir les charges de travail des utilisateurs entre deux dates
def get_user_workloads(email, password, start_date, end_date):
    url = 'http://localhost:8070'
    db = 'Odoo13'
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, email, password, {})

    if not uid:
        raise Exception("Échec de connexion avec les informations fournies.")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    try:
        workloads = models.execute_kw(
            db, uid, password,
            'user.workload', 'search_read',
            [[('workload_date', '>=', start_date), ('workload_date', '<=', end_date)]],
            {'fields': ['user_id', 'workload_hours', 'workload_date']}
        )
        return workloads
    except Exception as e:
        print("Erreur lors de la récupération des charges de travail:", e)
        return []

# Fonction pour mettre à jour ou créer une charge de travail pour un utilisateur dans Odoo
def update_user_workload(email, password, user_id, workload_date, new_total_hours):
    url = 'http://localhost:8070'
    db = 'Odoo13'
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, email, password, {})

    if not uid:
        raise Exception("Échec de connexion avec les informations fournies.")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Vérifier si une charge de travail existe déjà pour l'utilisateur à cette date
    workload = models.execute_kw(
        db, uid, password,
        'user.workload', 'search',
        [[('user_id', '=', user_id), ('workload_date', '=', workload_date)]]
    )
    
    if workload:
        # Si une charge de travail existe, on met à jour l'heure de travail
        models.execute_kw(
            db, uid, password,
            'user.workload', 'write',
            [workload, {'workload_hours': new_total_hours}]
        )
    else:
        # Sinon, on crée une nouvelle entrée pour cette charge de travail
        models.execute_kw(
            db, uid, password,
            'user.workload', 'create',
            [{'user_id': user_id, 'workload_date': workload_date, 'workload_hours': new_total_hours}]
        )

# Fonction principale pour assigner les tâches et mettre à jour la charge de travail dans Odoo
def assign_tasks(request, project_id, start_date):
    email = "iandrianina@gmail.com"  # Remplace par l'email d'utilisateur
    password = "qsdxwcazEr0****"   # Remplace par le mot de passe utilisateur

    json_projet = load_project_json(f"{project_id}.json")
    date_debut = datetime.strptime(start_date, '%Y-%m-%d').date()
    date_fin = calculate_end_date(json_projet, date_debut)

    # Obtenir les charges de travail des utilisateurs entre date_debut et date_fin
    workloads = get_user_workloads(email, password, start_date, date_fin.strftime('%Y-%m-%d'))
    
    # Créer un dictionnaire pour organiser les charges par utilisateur et date
    user_calendar = {}
    for workload in workloads:
        user_id = workload['user_id'][0]  # `user_id` est un tuple (id, nom)
        date = workload['workload_date']
        hours = workload['workload_hours']
        
        if user_id not in user_calendar:
            user_calendar[user_id] = []
        
        user_calendar[user_id].append({
            'date': date,
            'project': f'Projet {project_id}',
            'hours': hours
        })

    # Assignation des tâches
    assignments = []
    for tache in json_projet['taches']:
        if tache['id_utilisateur_assignable']:
            assigned_user_id = tache['id_utilisateur_assignable'][0]
            assignments.append({
                'id_tache': tache['id'],
                'assigned_user_id': assigned_user_id,
                'date_debut': date_debut.strftime('%Y-%m-%d'),
                'date_fin': date_fin.strftime('%Y-%m-%d')
            })

            # Calculer les heures de charge pour cet utilisateur et cette tâche
            assigned_hours = tache['duree']

            # Mettre à jour la charge de travail de l'utilisateur pour chaque date
            for single_date in (date_debut + timedelta(days=i) for i in range((date_fin - date_debut).days + 1)):
                if assigned_user_id in user_calendar:
                    # Calculer les heures totales pour la date
                    current_hours = sum(entry['hours'] for entry in user_calendar[assigned_user_id] if entry['date'] == single_date.strftime('%Y-%m-%d'))
                    new_total_hours = current_hours + assigned_hours
                    
                    # Pusher la charge de travail dans Odoo
                    update_user_workload(email, password, assigned_user_id, single_date.strftime('%Y-%m-%d'), new_total_hours)

    # Structure finale des données avec le calendrier
    response_data = {
        'date_fin': date_fin.strftime('%Y-%m-%d'),
        'assignments': assignments,
        'user_calendar': user_calendar
    }

    return JsonResponse(response_data)
