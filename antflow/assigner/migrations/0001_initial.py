# Generated by Django 3.2.25 on 2024-10-30 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Projet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('type_projet_id', models.IntegerField()),
                ('date_debut', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Tache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('duree', models.FloatField()),
                ('utilisateur_assigne_id', models.IntegerField()),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taches', to='assigner.projet')),
            ],
        ),
    ]