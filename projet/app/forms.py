#forms.py
from django import forms
from .models import Conge, Evaluation, Personnel

class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = '__all__'

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['evaluation_type', 'criteria', 'performance_rating', 'skills_developed', 'comments']
    
    # Customize criteria as a JSON field (could be a formset or a dynamic form in the frontend)
    criteria = forms.CharField(widget=forms.Textarea, required=False)



class CongeForm(forms.ModelForm):
    employe_identifier = forms.CharField(
        max_length=50,
        label="Nom ou ID de l'Employé",
        help_text="Tapez le nom ou l'ID de l'employé"
    )

    class Meta:
        model = Conge
        fields = ['type_conge', 'date_debut', 'date_fin', 'description']
        labels = {
            'type_conge': "Type de Congé",
            'date_debut': "Date de Début",
            'date_fin': "Date de Fin",
            'description': "Description",
        }
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_employe_identifier(self):
        identifier = self.cleaned_data['employe_identifier']
        try:
            if identifier.isdigit():
                employe = Personnel.objects.get(id=int(identifier))
            else:
                employe = Personnel.objects.get(name__iexact=identifier)
        except Personnel.DoesNotExist:
            raise forms.ValidationError("Employé introuvable. Vérifiez le nom ou l'ID.")
        return employe

    def save(self, commit=True):
        instance = super().save(commit=False)
        employe = self.cleaned_data['employe_identifier']
        instance.employe = employe  # Assign the correct employee to the Conge
        if commit:
            instance.save()
        return instance
