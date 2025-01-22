from django import forms
from .models import Contrat
from app.models import Personnel

class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = '__all__'

from django import forms
from .models import Contrat, Personnel

from django import forms
from .models import Contrat
from app.models import Personnel

class AjouterContratForm(forms.ModelForm):
    personnel_identifier = forms.CharField(
        max_length=50,
        label="Nom ou ID de l'Employé",
        required=True,
        help_text="Tapez le nom ou l'ID de l'employé pour l'associer au contrat"
    )

    class Meta:
        model = Contrat
        fields = ['date_debut', 'date_fin', 'type_contrat']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_personnel_identifier(self):
        identifier = self.cleaned_data['personnel_identifier']
        try:
            if identifier.isdigit():
                return Personnel.objects.get(id=int(identifier))
            else:
                return Personnel.objects.get(name__iexact=identifier)
        except Personnel.DoesNotExist:
            raise forms.ValidationError("Employé introuvable. Vérifiez le nom ou l'ID.")

    def save(self, commit=True):
        personnel = self.cleaned_data['personnel_identifier']
        instance = super().save(commit=False)
        instance.id_employe = personnel
        if commit:
            instance.save()
        return instance


class ModifierContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = ['date_debut', 'date_fin', 'type_contrat']  # Editable fields for modifying a contract
        labels = {
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'type_contrat': 'Type de contrat',
        }
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        """
        Save changes to the contract.
        """
        try:
            instance = super().save(commit=False)
            if commit:
                instance.save()
            return instance
        except Exception as e:
            raise forms.ValidationError(f"Erreur lors de la modification du contrat: {e}")
