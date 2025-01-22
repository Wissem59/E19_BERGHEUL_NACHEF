from django.db import models
from app.models import Service
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Recrutement(models.Model):
    id_poste = models.AutoField(primary_key=True)
    id_service = models.ForeignKey(Service, on_delete=models.CASCADE)  # Cascade delete
    description = models.CharField(max_length=200)
    titre = models.CharField(max_length=50)
    exigences = models.CharField(max_length=200)
    statut = models.CharField(max_length=50)
    date_publication = models.DateField()

class Offre_emploi(models.Model):
    class StatutChoices(models.TextChoices):
        ACTIF = 'Actif', _('Active')
        EXPIRE = 'Expire', _('Expired')
        EN_ATTENTE = 'En attente', _('Pending')

    id_offre = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=300, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"), default='No description provided')
    statut = models.CharField(
        max_length=20,
        choices=StatutChoices.choices,
        default=StatutChoices.EN_ATTENTE,
        verbose_name=_("Status"),
    )
    date_publication = models.DateField(verbose_name=_("Publication Date"))
    date_expiration = models.DateField(null=True, blank=True, verbose_name=_("Expiration Date"))
    lieu = models.CharField(max_length=255, verbose_name=_("Location"), default="Not specified")
    type_contrat = models.CharField(max_length=100, verbose_name=_("Contract Type"), default="Not specified")

    class Meta:
        verbose_name = _("Job Offer")
        verbose_name_plural = _("Job Offers")
        ordering = ['-date_publication']

    def __str__(self):
        return f"{self.titre} ({self.get_statut_display()})"

    def is_active(self):
        if self.date_expiration:
            return self.date_expiration >= timezone.now().date()
        return self.statut == self.StatutChoices.ACTIF

class Candidature(models.Model):
    class StatutCandidatureChoices(models.TextChoices):
        EN_ATTENTE = 'En attente', _('En attente')
        ACCEPTE = 'Accepté', _('Accepté')
        REJETE = 'Rejeté', _('Rejeté')

    id_candidature = models.AutoField(primary_key=True)
    id_offre = models.ForeignKey(Offre_emploi, on_delete=models.CASCADE, related_name="candidatures")  # Cascade delete
    nom_candidat = models.CharField(max_length=100, verbose_name=_("Candidate Name"))
    email_candidat = models.EmailField(verbose_name=_("Candidate Email"), null=True, blank=True)
    telephone_candidat = models.IntegerField(verbose_name=_("Candidate Telephone"), null=True, blank=True)
    cv = models.FileField(upload_to='candidatures/cv/', verbose_name=_("Resume"))
    lettre_motivation = models.TextField(verbose_name=_("Cover Letter"), null=True, blank=True)
    date_candidature = models.DateTimeField(default=timezone.now, verbose_name=_("Application Date"))
    statut_candidature = models.CharField(
        max_length=20,
        choices=StatutCandidatureChoices.choices,
        default=StatutCandidatureChoices.EN_ATTENTE,
        verbose_name=_("Application Status"),
    )

    class Meta:
        verbose_name = _("Candidature")
        verbose_name_plural = _("Candidatures")
        ordering = ['-date_candidature']

    def __str__(self):
        return f"{self.nom_candidat} - {self.id_offre.titre} ({self.get_statut_candidature_display()})"

class Entretien(models.Model):
    id_entretien = models.AutoField(primary_key=True)
    id_candidature = models.ForeignKey(Candidature, on_delete=models.CASCADE, related_name="entretiens")  # Cascade delete
    date_entretien = models.DateTimeField(verbose_name=_("Interview Date"))
    lieu_entretien = models.CharField(max_length=255, verbose_name=_("Interview Location"))
    statut_entretien = models.CharField(max_length=50, verbose_name=_("Interview Status"), default="Scheduled")
    notes = models.TextField(verbose_name=_("Interview Notes"), null=True, blank=True)

    class Meta:
        verbose_name = _("Entretien")
        verbose_name_plural = _("Entretiens")

    def __str__(self):
        return f"Entretien pour {self.id_candidature.nom_candidat} - {self.date_entretien}"
