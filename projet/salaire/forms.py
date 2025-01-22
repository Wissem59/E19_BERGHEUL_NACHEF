from django import forms
from .models import Presence
from app.models import Personnel
from salaire import views

class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = '__all__'

class AjouterAbsenceForm(forms.ModelForm):
    # Custom field for Personnel identification
    personnel_identifier = forms.CharField(
        max_length=50,
        label="Nom ou ID de l'Employé",
        help_text="Tapez le nom ou l'ID de l'employé"
    )

    class Meta:
        model = Presence
        fields = ['date_absence', 'is_absent']  # Fields from the Presence model
        labels = {
            'date_absence': 'Date d\'absence',
            'is_absent': 'Absence',
        }
        widgets = {
            'date_absence': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_personnel_identifier(self):
        """
        Validate the personnel_identifier to ensure it matches an existing Personnel.
        """
        identifier = self.cleaned_data['personnel_identifier']
        try:
            if identifier.isdigit():
                personnel = Personnel.objects.get(id=int(identifier))
            else:
                personnel = Personnel.objects.get(name__iexact=identifier)
        except Personnel.DoesNotExist:
            raise forms.ValidationError("Employé introuvable. Vérifiez le nom ou l'ID.")
        return personnel

    def save(self, commit=True):
        try:
        # Validated Personnel instance
            personnel = self.cleaned_data['personnel_identifier']
            absence_date = self.cleaned_data.get('date_absence')

        # Call ajouter_absences to handle the logic
            views.ajouter_absences(personnel, absence_date=absence_date)

        # Save the form instance
            instance = super().save(commit=False)
            if commit:
                instance.save()
            return instance
        except Exception as e:
            raise forms.ValidationError(f"Erreur lors de l'ajout de l'absence: {e}")

class ModifierAbsenceForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = ['is_absent']  # Only include the 'is_absent' checkbox field
        labels = {
            'is_absent': 'Absence',
        }

    def save(self, commit=True):
        try:
            # Call the parent's save method to update the 'is_absent' status
            instance = super().save(commit=False)
            if commit:
                instance.save()
            return instance
        except Exception as e:
            raise forms.ValidationError(f"Erreur lors de l'ajout de l'absence: {e}")