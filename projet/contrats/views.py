from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Contrat
from app.models import Personnel
from .forms import AjouterContratForm, ModifierContratForm


# List of contracts
@login_required
def liste_contrats(request):
    # Retrieve search parameters from the GET request
    id_employe_query = request.GET.get('id_employe', '').strip()
    nom_employe_query = request.GET.get('nom_employe', '').strip()
    date_query = request.GET.get('q', '').strip()
    service_filter = request.GET.get('serviceFilter', '').strip()
    type_filter = request.GET.get('typeFilter', '').strip()
    start_date_filter = request.GET.get('startDateFilter', '').strip()
    end_date_filter = request.GET.get('endDateFilter', '').strip()

    # Fetch all contracts
    contrats = Contrat.objects.all()

    # Apply search filters
    if id_employe_query:
        contrats = contrats.filter(id_employe__id__icontains=id_employe_query)
    if nom_employe_query:
        contrats = contrats.filter(id_employe__name__icontains=nom_employe_query)
    if date_query:
        contrats = contrats.filter(date_Contrat=date_query)
    if service_filter:
        contrats = contrats.filter(id_employe__service__icontains=service_filter)
    if type_filter:
        contrats = contrats.filter(type_contrat__iexact=type_filter)
    if start_date_filter:
        contrats = contrats.filter(date_debut__gte=start_date_filter)
    if end_date_filter:
        contrats = contrats.filter(date_fin__lte=end_date_filter)

    # Build the contrats data for rendering
    contrats_data = [get_contrat(contrat.id, False) for contrat in contrats]

    # Render the template with the filtered data
    return render(request, 'contrats/liste_contrats.html', {
        'contrats': contrats_data,
        'current_url': request.path.lstrip('/'),
    })


# Archive contracts
@login_required
def archive_contrats(request):
    # Retrieve search parameters from the GET request
    id_employe_query = request.GET.get('id_employe', '').strip()
    nom_employe_query = request.GET.get('nom_employe', '').strip()
    date_query = request.GET.get('q', '').strip()

    contrats = Contrat.objects.all()
    
    # Search logic
    if id_employe_query:
        contrats = contrats.filter(id_employe__id__icontains=id_employe_query)
    if nom_employe_query:
        contrats = contrats.filter(id_employe__name__icontains=nom_employe_query)
    if date_query:
        contrats = contrats.filter(date_Contrat=date_query)

    # Build the contrats data for rendering
    contrats_data = [get_contrat(contrat.id, True) for contrat in contrats]
    return render(request, 'contrats/archive_contrats.html', {'contrats': contrats_data
                                                              , 'current_url': request.path.lstrip('/')})

# Add a new contract
@login_required
def ajouter_contrat(request):
    if request.method == 'POST':
        form = AjouterContratForm(request.POST)
        if form.is_valid():
            try:
                # Ensure no active contract exists for the employee
                employe = form.cleaned_data['id_employe']
                valider_contrat_unique(employe)

                # Save the contract
                instance = form.save()
                print(f"Contract added: {instance}")
                return redirect('liste_contrats')
            except ValidationError as e:
                return render(request, 'contrats/ajouter_contrat.html', {'form': form, 'message': f"Erreur de validation: {e.message}"})
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return render(request, 'contrats/ajouter_contrat.html', {'form': form, 'message': f"Erreur inattendue: {str(e)}"})
        else:
            print("Form errors:", form.errors)
            return render(request, 'contrats/ajouter_contrat.html', {'form': form, 'message': "Veuillez corriger les erreurs ci-dessus."})
    else:
        form = AjouterContratForm()

    return render(request, 'contrats/ajouter_contrat.html', {'form': form
                                                             , 'current_url': request.path.lstrip('/')})

# Modify an existing contract
@login_required
def modifier_contrat(request, contrat_id):
    fetched_contrat = get_object_or_404(Contrat, id=contrat_id)

    if request.method == 'POST':
        form = ModifierContratForm(request.POST, instance=fetched_contrat)
        if form.is_valid():
            try:
                # Validate contract updates
                employe = form.cleaned_data['id_employe']
                valider_contrat_unique(employe)

                form.save()
                return redirect('liste_contrats')
            except ValidationError as e:
                return render(request, "Contrats/modifier_Contrat.html", {
                    "form": form,
                    "message": f"Erreur: {e.message}",
                    "contrat": fetched_contrat
                })
    else:
        form = ModifierContratForm(instance=fetched_contrat)

    contrat_data = get_contrat(contrat_id, False)
    return render(request, "Contrats/modifier_Contrat.html", {"form": form, "contrat": contrat_data
                                                              , 'current_url': request.path.lstrip('/')})

# Archive a contract (mark as archived)
@login_required
def supprimer_contrat(request, contrat_id):
    contrat_info = get_object_or_404(Contrat, id=contrat_id)
    if request.method == 'POST':
        contrat_info.archive = True
        contrat_info.save()
        return redirect('liste_contrats')
    return render(request, 'contrats/supprimer_contrat.html', {'contrat': get_contrat(contrat_id)
                                                               , 'current_url': request.path.lstrip('/')})

# View a contract's details
@login_required
def consulter_contrat(request, contrat_id):
    contrat = get_contrat(contrat_id, False)
    return render(request, 'contrats/consulter_contrat.html', {'contrat': contrat
                                                               , 'current_url': request.path.lstrip('/')})

# Renew a contract
@login_required
def renouveler_contrat(request, contrat_id):
    # Fetch the contract and the related employee
    contrat = get_object_or_404(Contrat, id=contrat_id)
    employe = contrat.id_employe  # Access the employee via the contract's foreign key

    if request.method == 'POST':
        # Get POST data from the form
        contract_type = request.POST.get('contract_type')
        new_contract_start_date = request.POST.get('new_contract_start_date')
        contract_duration = request.POST.get('contract_duration')
        renewal_comments = request.POST.get('renewal_comments', '')

        # Validate input fields
        if not new_contract_start_date or not contract_duration:
            return render(request, 'contrats/renouveler_contrat.html', {
                'employe': employe,
                'contrat': contrat,
                'message': "Veuillez remplir tous les champs requis."
            })

        try:
            # Convert string dates to actual date objects
            start_date = datetime.strptime(new_contract_start_date, '%Y-%m-%d').date()
            duration_months = int(contract_duration)
            end_date = start_date + relativedelta(months=duration_months)

            # Create the new contract for renewal
            new_contrat = Contrat.objects.create(
                id_employe=employe,
                type_contrat=contract_type,
                date_debut=start_date,
                date_fin=end_date,
                commentaires=renewal_comments
            )

            messages.success(request, "Le contrat a été renouvelé avec succès.")
            return redirect('liste_contrats')
        except ValidationError as e:
            print(f"Error: {e}")
            return render(request, 'contrats/renouveler_contrat.html', {
                'employe': employe,
                'contrat': contrat,
                'message': f"Erreur lors du renouvellement: {e.message}"
            })

    else:
        # Prepopulate with current contract data
        return render(request, 'contrats/renouveler_contrat.html', {
            'employe': employe,
            'contrat': contrat, 'current_url': request.path.lstrip('/')
        })

# Helper function to get contract data
def get_contrat(contrat_id, archive_status=None):
    try:
        query_params = {'id': contrat_id}
        if archive_status is not None:
            query_params['archive'] = archive_status
        
        contrat_info = Contrat.objects.get(**query_params)
        personnel = contrat_info.id_employe
        service = personnel.IdService
        return {
            'id': contrat_info.id,
            'matricule': personnel.id,
            'nom': personnel.name,
            'service_id': service.IdService,
            'nom_service': service.nameservice,
            'poste': personnel.Position,
            'date_debut': contrat_info.date_debut,
            'date_fin': contrat_info.date_fin,
            'type_contrat': contrat_info.type_contrat,
            'archive': contrat_info.archive
        }
    except (Contrat.DoesNotExist, AttributeError):
        return {}

# Additional helper to ensure an employee only has one active contract at a time
def valider_contrat_unique(employe):
    """
    Ensure that an employee can only have one active contract at the same time.
    """
    active_contrats = Contrat.objects.filter(id_employe=employe, archive=False)
    if active_contrats.exists():
        raise ValidationError("L'employé a déjà un contrat actif. Un seul contrat est autorisé à la fois.")

@login_required
def suivi_periode_dessai(request):
    today_date = timezone.now().date()
    next_renewal_date = today_date + timezone.timedelta(days=30)

    # Fetch query parameters for searching and filtering
    id_employe_query = request.GET.get('id_employe', '').strip()
    nom_employe_query = request.GET.get('nom_employe', '').strip()
    date_query = request.GET.get('q', '').strip()
    service_filter = request.GET.get('serviceFilter', '').strip()
    type_filter = request.GET.get('typeFilter', '').strip()
    start_date_filter = request.GET.get('startDateFilter', '').strip()
    end_date_filter = request.GET.get('endDateFilter', '').strip()

    # Base queryset
    contrats = Contrat.objects.select_related('id_employe').filter(
        archive=False,  # Exclude archived contracts
        periode_essai_fin__isnull=False,  # Only contracts with a defined probation end date
        periode_essai_fin__gte=today_date  # Probation end date is not in the past
    )

    # Apply filters
    if id_employe_query:
        contrats = contrats.filter(id_employe__id=id_employe_query)

    if nom_employe_query:
        contrats = contrats.filter(id_employe__nom__icontains=nom_employe_query)

    if date_query:
        contrats = contrats.filter(
            Q(date_debut__icontains=date_query) | Q(date_fin__icontains=date_query)
        )

    if service_filter:
        contrats = contrats.filter(id_employe__service__icontains=service_filter)

    if type_filter:
        contrats = contrats.filter(type_contrat=type_filter)

    if start_date_filter:
        contrats = contrats.filter(date_debut__gte=start_date_filter)

    if end_date_filter:
        contrats = contrats.filter(date_fin__lte=end_date_filter)

    return render(request, 'suivi_periode_dessai.html', {
        'contrats': contrats,
        'today_date': today_date,
        'next_renewal_date': next_renewal_date,
        'current_url': request.path.lstrip('/'),
    })


@login_required
def terminer_contrat(request, contrat_id):
    contrat = get_object_or_404(Contrat, id=contrat_id)  # Get the contract by its ID

    if request.method == 'POST':
        # Archive the contract
        contrat.archiver_contrat()  # Use the existing method to archive the contract
        
        # Add termination reason and optional comments
        termination_reason = request.POST.get('termination_reason')
        termination_comments = request.POST.get('termination_comments')
        
        # Save termination details
        contrat.termination_reason = termination_reason
        contrat.termination_comments = termination_comments
        contrat.save()
        
        return HttpResponseRedirect(reverse('liste_contrats'))  # Redirect to the contracts list page
    
    return render(request, 'contrats/terminer_contrat.html', {
        'contrat': contrat, 'current_url': request.path.lstrip('/')
    })

@login_required
def suivi_periode_dessai(request):
    today_date = timezone.now().date()
    next_renewal_date = today_date + timezone.timedelta(days=30)  # Example: next 30 days

    contrats = Contrat.objects.filter(archive=False)  # Exclude archived contracts

    context = {
        'contrats': contrats,
        'today_date': today_date,
        'next_renewal_date': next_renewal_date,
        'current_url': request.path.lstrip('/')
    }
    return render(request, 'contrats/suivi_periode_dessai.html', context)
