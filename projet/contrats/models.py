from django.db import models
from app.models import Service, Personnel
from django.utils import timezone

class Contrat(models.Model):
    TYPES_CONTRAT = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('STAGE', 'Stage'),
        ('AUTRE', 'Autre'),
    ]
    id_employe = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='contrats')  # Cascade delete when Personnel is deleted
    type_contrat = models.CharField(max_length=6, choices=TYPES_CONTRAT)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)  # Null pour les contrats indéterminés
    periode_essai_debut = models.DateField(null=True, blank=True)
    periode_essai_fin = models.DateField(null=True, blank=True)
    alerte_renouvellement_envoyee = models.BooleanField(default=False)  # Indicateur pour alertes de renouvellement
    archive = models.BooleanField(default=False)
    fichier_contrat = models.FileField(upload_to='contrats/', null=True, blank=True)

    def __str__(self):
        return f"{self.id_employe.name} - {self.get_type_contrat_display()}"

    def est_periode_essai_terminee(self):
        if self.periode_essai_fin:
            return timezone.now().date() > self.periode_essai_fin
        return False

    def est_renouvellement_du(self):
        if self.date_fin and not self.alerte_renouvellement_envoyee:
            return timezone.now().date() >= self.date_fin
        return False

    def archiver_contrat(self):
        self.archive = True
        self.save()

    def envoyer_alerte_renouvellement(self):
        # Logique pour envoyer une alerte de renouvellement
        self.alerte_renouvellement_envoyee = True 
        self.save()
