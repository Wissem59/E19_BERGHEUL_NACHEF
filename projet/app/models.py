from django.db import models
from django.core.validators import RegexValidator  
from datetime import date


class Service(models.Model):
    IdService = models.CharField(max_length=50, primary_key=True)
    nameservice = models.CharField(max_length=50) 

    def __str__(self):
        return self.IdService


class Personnel(models.Model): 
    name = models.CharField(max_length=50) 
    Email = models.EmailField(max_length=254)
    
    # Phone number validation to ensure it starts with 05, 06, or 07 and is 10 digits long
    phone_validator = RegexValidator(
        regex=r'^(05|06|07)\d{8}$',
        message="Phone number must be 10 digits long and start with 05, 06, or 07."
    )
    Phone = models.CharField(max_length=10, validators=[phone_validator])  # Apply the validator to the Phone field
    date_naissance = models.DateField(null=False)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Gender", default='M')
    Position = models.CharField(max_length=40)
    skills = models.CharField(max_length=254) 
    training = models.CharField(max_length=254)
    IdService = models.ForeignKey(Service, on_delete=models.CASCADE)
    hireDate = models.DateField() 
    Adresse = models.CharField(max_length=254)
    jours_annuels = models.IntegerField(default=30, verbose_name="Jours de Congé Annuel")  # Default to 30 days
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.jours_restants < 0:
            self.jours_restants = 0  # Ensure no negative values
        super(Personnel, self).save(*args, **kwargs)

class Evaluation(models.Model):
    employee = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name="evaluations")  # Added on_delete cascade
    date = models.DateField(auto_now_add=True)
    evaluation_type = models.CharField(
        max_length=20,
        choices=[('Annual', 'Annual'), ('Semi-Annual', 'Semi-Annual')],
        default='Annual'
    )
    criteria = models.JSONField(default=dict)  # Customizable evaluation criteria in JSON format
    performance_rating = models.IntegerField()  # Performance rating, e.g., 1-10
    skills_developed = models.TextField(blank=True)  # Optional field for developed skills
    comments = models.TextField(blank=True)  # Manager's comments

    def __str__(self):
        return f"Evaluation for {self.employee.name} on {self.date}"


class Conge(models.Model):
    TYPES_CONGES = [
        ('Annuel', 'Congé Annuel'),
        ('Maladie', 'Congé Maladie'),
        ('Maternité', 'Congé Maternité'),
        ('Paternité', 'Congé Paternité'),
        ('Sans Solde', 'Congé Sans Solde'),
        ('Autre', 'Autre'),
    ]
    employe = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='conges')
    type_conge = models.CharField(max_length=20, choices=TYPES_CONGES)
    date_debut = models.DateField(verbose_name="Date de Début")
    date_fin = models.DateField(verbose_name="Date de Fin")
    jours_utilises = models.IntegerField(verbose_name="Jours Utilisés", editable=False)
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    
    def save(self, *args, **kwargs):
        self.jours_utilises = (self.date_fin - self.date_debut).days + 1
        super().save(*args, **kwargs)
    
    @staticmethod
    def calcul_jours_restants(employe):
        conges_annuels = Conge.objects.filter(employe=employe, type_conge='Annuel')
        jours_utilises_total = sum(conge.jours_utilises for conge in conges_annuels)
        return employe.jours_annuels - jours_utilises_total

    def __str__(self):
        return f"{self.employe.name} - {self.type_conge}"
