from rest_framework import serializers
from .models import Projet, Tache

class ProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = ['id', 'nom', 'type_projet_id', 'date_debut']

class TacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tache
        fields = ['id', 'nom', 'duree', 'projet', 'id_utilisateur_assignable', 'id_tache_dependance']
