from django.db import models
from app.models import Personnel
from django.core.exceptions import ValidationError
from datetime import datetime


class Salaire(models.Model):
    id_salaire = models.AutoField(primary_key=True)
    id_employe = models.ForeignKey(Personnel, on_delete=models.CASCADE)  # Cascade delete when Personnel is deleted
    date_paie = models.DateField()  # The payment date
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total salary amount
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, default=30000.00)  # Base salary
    salaire_jour = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)  # Daily salary
    absences = models.IntegerField(default=0)  # Number of absences
    massrouf_mensuel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Monthly advance amount

    # Bonus fields
    prime_performance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Performance bonus
    prime_festive = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Festive bonus
    prime_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total bonuses

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['id_employe', 'date_paie'],
                name='unique_salaire_per_employee_per_month'
            )
        ]

    def save(self, *args, **kwargs):
        # Set the payment date to the first day of the month
        self.date_paie = self.date_paie.replace(day=1)

        # Calculate total bonuses
        self.prime_total = self.prime_performance + self.prime_festive

        # Calculate the final salary by considering absences and the advance amount
        absence_penalty = self.absences * self.salaire_jour
        self.montant = (
            self.salaire_base - absence_penalty - self.massrouf_mensuel + self.prime_total
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salaire {self.id_salaire}: {self.id_employe.name} - {self.date_paie.strftime('%Y-%m')}"


class Massrouf(models.Model):
    massrouf_fois = models.IntegerField(default=0)  # Number of advances requested
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Advance amount
    annee = models.IntegerField(default=datetime.now().year)  # Year of the advance request
    id_employe = models.ForeignKey(Personnel, on_delete=models.CASCADE)  # Cascade delete when Personnel is deleted

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['annee', 'id_employe'], name='unique_annee_employe')
        ]

    def save(self, *args, **kwargs):
        # Check if the employee has already requested more than 2 advances in a year
        if self.massrouf_fois >= 2:
            raise ValidationError("Un employé ne peut demander qu'un maximum de 2 avances par an.")
        
        # Increment the number of advance requests
        self.massrouf_fois += 1
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Massrouf {self.massrouf_fois} for {self.id_employe} in {self.annee}"


class Presence(models.Model):
    date_absence = models.DateField()  # Date of absence
    id_employe = models.ForeignKey(Personnel, on_delete=models.CASCADE)  # Cascade delete when Personnel is deleted
    is_absent = models.BooleanField(default=True)  # Indicates if the employee was absent

    class Meta:
        unique_together = ('date_absence', 'id_employe')  # Ensure unique combination of date and employee
        verbose_name = "Presence"
        verbose_name_plural = "Presences"

    def save(self, *args, **kwargs):
        # Prevent absences from being recorded on weekends
        if self.date_absence.weekday() in [5, 6]:  # Weekends (Saturday=5, Sunday=6)
            raise ValidationError("Les absences ne peuvent être enregistrées que pour les jours ouvrables.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Absence on {self.date_absence} for {self.id_employe.name}"
