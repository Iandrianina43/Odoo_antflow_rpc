from django.db import models

class Projet(models.Model):
    nom = models.CharField(max_length=100)
    type_projet_id = models.IntegerField()  # ID du type de projet
    date_debut = models.DateField()

    def __str__(self):
        return self.nom

class Tache(models.Model):
    nom = models.CharField(max_length=100)
    duree = models.FloatField()  # Durée en heures (ex. : 0,83 h)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='taches')
    utilisateur_assigne_id = models.IntegerField()  # ID de l'utilisateur assigné

    def __str__(self):
        return f"{self.nom} - {self.duree}h"
