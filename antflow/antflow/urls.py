from django.contrib import admin
from django.urls import path, include  # Assure-toi d'importer 'include'
from assigner.views import assign_tasks

urlpatterns = [
    path('assign-tasks/<int:project_id>/<str:start_date>/', assign_tasks, name='assign_tasks'),
    # Ajoute d'autres URL ici si nécessaire
    path('api/', include('assigner.urls')),  # Si tu as d'autres URLs
]
