from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.translation import gettext as _
from django.utils.timezone import now
from datetime import datetime, date
from .models import Offre_emploi, Candidature, Entretien
from django.contrib.auth.decorators import login_required

@login_required
def liste_offres_emploi(request):
    # Retrieve search parameters from the GET request
    titre_query = request.GET.get('titre', '').strip()
    statut_query = request.GET.get('statut', '').strip()
    date_publication_query = request.GET.get('date_publication', '').strip()
    date_expiration_query = request.GET.get('date_expiration', '').strip()

    offres_emploi = Offre_emploi.objects.all()

    # Search logic
    if titre_query:
        offres_emploi = offres_emploi.filter(titre__icontains=titre_query)
    if statut_query:
        offres_emploi = offres_emploi.filter(statut__iexact=statut_query)
    
    # Handle date filtering if provided
    if date_publication_query:
        try:
            # Convert string to date format
            date_publication = datetime.strptime(date_publication_query, '%Y-%m-%d').date()
            offres_emploi = offres_emploi.filter(date_publication=date_publication)
        except ValueError:
            # Handle invalid date format gracefully
            pass
    
    if date_expiration_query:
        try:
            # Convert string to date format
            date_expiration = datetime.strptime(date_expiration_query, '%Y-%m-%d').date()
            offres_emploi = offres_emploi.filter(date_expiration=date_expiration)
        except ValueError:
            # Handle invalid date format gracefully
            pass

    # Build the Recrutements data for rendering
    offres_emploi_data = []
    for offre_emploi in offres_emploi:
        # Check if the current date is past the expiration date
        if date.today() > offre_emploi.date_expiration:
            offre_emploi.statut = "Expire"
            offre_emploi.save()
        
        offres_emploi_data.append({
            'id': offre_emploi.id_offre,
            'titre': offre_emploi.titre,
            'description': offre_emploi.description,
            'statut': offre_emploi.statut,
            'date_publication': offre_emploi.date_publication,
            'date_expiration': offre_emploi.date_expiration,
            'lieu': offre_emploi.lieu,
            'type_contrat': offre_emploi.type_contrat
        })
    print(offres_emploi_data)

    # Pass the filtered list of offres_emploi to the template
    return render(request, 'offre_emploi/liste_offres_emploi.html', {'offres_emploi': offres_emploi_data
                                                                     , 'current_url': request.path.lstrip('/')})

@login_required
def consulter_offre_emploi(request, offre_emploi):
    fetched_offre_emploi = get_object_or_404(Offre_emploi, id_offre=offre_emploi)
    offre_emploi_info = ({
            'id_offre': fetched_offre_emploi.id_offre,
            'titre': fetched_offre_emploi.titre,
            'description': fetched_offre_emploi.description,
            'statut': fetched_offre_emploi.statut,
            'date_publication': fetched_offre_emploi.date_publication,
            'date_expiration': fetched_offre_emploi.date_expiration,
            'lieu': fetched_offre_emploi.lieu,
            'type_contrat': fetched_offre_emploi.type_contrat
        })
    return render(request, 'offre_emploi/consulter_offre_emploi.html', {'offre_emploi': offre_emploi_info
                                                                        , 'current_url': request.path.lstrip('/')})

@login_required
def publier_offre_emploi(request):
    if request.method == "POST":
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description', '').strip()
        lieu = request.POST.get('lieu', '').strip()
        type_contrat = request.POST.get('type_contrat', '').strip()
        date_publication = now().date()
        date_expiration = request.POST.get('date_expiration', '').strip()

        # Validate required fields
        if not titre or not description or not lieu or not type_contrat or not date_expiration:
            return render(request, 'offre_emploi/publier_offre_emploi.html', {
                'error_message': 'Tous les champs sont obligatoires.'
            })

        try:
            # Create new job offer
            offre_emploi = Offre_emploi.objects.create(
                titre=titre,
                description=description,
                lieu=lieu,
                type_contrat=type_contrat,
                statut=Offre_emploi.StatutChoices.ACTIF,
                date_publication=date_publication,
                date_expiration=date_expiration
            )
            return redirect('liste_offre_emploi')
        except Exception as e:
            return render(request, 'offre_emploi/publier_offre_emploi.html', {
                'error_message': 'Une erreur s\'est produite. Veuillez réessayer.',
                'exception': str(e)
            })

    return render(request, 'offre_emploi/publier_offre_emploi.html', { 'current_url': request.path.lstrip('/')})

@login_required
def modifier_offre_emploi(request, offre_emploi):
    offre_emploi_instance = get_object_or_404(Offre_emploi, id_offre=offre_emploi)

    if request.method == "POST":
        offre_emploi_instance.titre = request.POST.get('titre', '').strip()
        offre_emploi_instance.description = request.POST.get('description', '').strip()
        offre_emploi_instance.lieu = request.POST.get('lieu', '').strip()
        offre_emploi_instance.type_contrat = request.POST.get('type_contrat', '').strip()
        offre_emploi_instance.date_expiration = request.POST.get('date_expiration', '').strip()
        offre_emploi_instance.statut = request.POST.get('statut', '').strip()  # New line for statut

        # Validate required fields
        if not offre_emploi_instance.titre or not offre_emploi_instance.description or not offre_emploi_instance.lieu or not offre_emploi_instance.type_contrat or not offre_emploi_instance.statut:
            return render(request, 'offre_emploi/modifier_offre_emploi.html', {
                'offre_emploi': offre_emploi_instance,
                'error_message': 'Tous les champs sont obligatoires.'
            })

        try:
            # Save updated offer
            offre_emploi_instance.save()
            return redirect('/Offre_emploi/liste_offres_emploi', offre_emploi=offre_emploi_instance.id_offre)
        except Exception as e:
            return render(request, 'offre_emploi/modifier_offre_emploi.html', {
                'offre_emploi': offre_emploi_instance,
                'error_message': 'Une erreur s\'est produite. Veuillez réessayer.',
                'exception': str(e)
            })

    return render(request, 'offre_emploi/modifier_offre_emploi.html', {'offre_emploi': offre_emploi_instance
                                                                       , 'current_url': request.path.lstrip('/')})

@login_required
def supprimer_offre_emploi(request, offre_emploi):
    offre_emploi_instance = get_object_or_404(Offre_emploi, id_offre=offre_emploi)

    if request.method == "POST":
        try:
            offre_emploi_instance.delete()
            return redirect('liste_offre_emploi')
        except Exception as e:
            return render(request, 'offre_emploi/consulter_offre_emploi.html', {
                'offre_emploi': offre_emploi_instance,
                'error_message': 'Une erreur s\'est produite lors de la suppression.',
                'exception': str(e)
            })

    return render(request, 'offre_emploi/supprimer_offre_emploi.html', {'offre_emploi': offre_emploi_instance
                                                                        , 'current_url': request.path.lstrip('/')})

@login_required
def soumettre_candidature(request):
    if request.method == 'POST':
        nom_candidat = request.POST.get('nom_candidat')
        email_candidat = request.POST.get('email_candidat')
        lettre_motivation = request.POST.get('lettre_motivation', '')
        id_offre = request.POST.get('id_offre')
        cv = request.FILES.get('cv')

        if not nom_candidat or not email_candidat or not id_offre or not cv:
            messages.error(request, _("Tous les champs obligatoires doivent être remplis."))
            return redirect('soumettre_candidature')

        try:
            offre = Offre_emploi.objects.get(pk=id_offre)
        except Offre_emploi.DoesNotExist:
            messages.error(request, _("L'offre sélectionnée n'existe pas."))
            return redirect('soumettre_candidature')

        # Save the CV file
        fs = FileSystemStorage()
        filename = fs.save(cv.name, cv)
        cv_url = fs.url(filename)

        # Save the Candidature
        Candidature.objects.create(
            nom_candidat=nom_candidat,
            email_candidat=email_candidat,
            lettre_motivation=lettre_motivation,
            id_offre=offre,
            cv=filename,
        )

        messages.success(request, _("Votre candidature a été soumise avec succès."))
        return redirect('offres_list')  # Redirect to the job offers list or another page.

    offres = Offre_emploi.objects.filter(statut=Offre_emploi.StatutChoices.ACTIF)
    return render(request, 'candidature/soumettre_candidature.html', {'offres': offres
                                                                      , 'current_url': request.path.lstrip('/')})

@login_required
def liste_candidats(request):
    # Retrieve search parameters from the GET request
    nom_query = request.GET.get('candidate_name', '').strip()
    email_query = request.GET.get('email', '').strip()
    statut_query = request.GET.get('status', '').strip()

    candidats = Candidature.objects.all().order_by('id_candidature')

    # Search logic
    if nom_query:
        candidats = candidats.filter(nom_candidat__icontains=nom_query)
    if email_query:
        candidats = candidats.filter(email_candidat__icontains=email_query)
    if statut_query:
        candidats = candidats.filter(statut_candidature__icontains=statut_query)

    # Build the Candidature data for rendering
    candidats_data = []
    for candidat in candidats:
        candidats_data.append({
            'id': candidat.id_candidature,
            'nom': candidat.nom_candidat,
            'email': candidat.email_candidat,
            'telephone': candidat.telephone_candidat,
            'poste': candidat.id_offre.titre if candidat.id_offre else "Non spécifié",
            'date_soumission': candidat.date_candidature,
            'cv': candidat.cv.url if candidat.cv else None,
            'lettre_motivation': candidat.lettre_motivation,
            'statut': candidat.statut_candidature,
        })

    # Pass the filtered list of candidats to the template
    return render(request, 'candidature/liste_candidats.html', {'candidats': candidats_data
                                                                , 'current_url': request.path.lstrip('/')})

@login_required
def consulter_candidature(request, candidature):
    fetched_candidature = get_object_or_404(Candidature, id_candidature=candidature)
    
    candidature_info = {
        'id_candidature': fetched_candidature.id_candidature,
        'nom_candidat': fetched_candidature.nom_candidat,
        'email_candidat': fetched_candidature.email_candidat,
        'telephone_candidat': fetched_candidature.telephone_candidat,
        'poste': fetched_candidature.id_offre.titre if fetched_candidature.id_offre else "Non spécifié",
        'date_candidature': fetched_candidature.date_candidature,
        'cv': fetched_candidature.cv.url if fetched_candidature.cv else None,
        'lettre_motivation': fetched_candidature.lettre_motivation,
        'statut': fetched_candidature.statut_candidature,
    }
    
    return render(request, 'candidature/consulter_candidature.html', {'candidature': candidature_info
                                                                      , 'current_url': request.path.lstrip('/')})

@login_required
def modifier_statut_candidature(request, candidature):
    fetched_candidature = get_object_or_404(Candidature, id_candidature=candidature)

    if request.method == "POST":
        fetched_candidature.statut_candidature = request.POST.get('statut_candidature', '').strip()

        # Validate required fields
        if not fetched_candidature.statut_candidature:
            return render(request, 'candidature/modifier_statut_candidature.html', {
                'candidature': fetched_candidature,
                'error_message': 'Le statut de la candidature est obligatoire.'
            })

        try:
            # Save the updated candidature status
            fetched_candidature.save()
            return redirect('/Condidature/liste_candidats')  # Redirect to the list of candidatures
        except Exception as e:
            return render(request, 'candidature/modifier_statut_candidature.html', {
                'candidature': fetched_candidature,
                'error_message': 'Une erreur s\'est produite. Veuillez réessayer.',
                'exception': str(e)
            })

    return render(request, 'candidature/modifier_statut_candidature.html', {'candidature': fetched_candidature
                                                                            , 'current_url': request.path.lstrip('/')})

@login_required
def liste_entretiens(request):
    # Retrieve search parameters from the GET request
    candidat_query = request.GET.get('candidat', '').strip()
    statut_query = request.GET.get('statut', '').strip()
    date_entretien_query = request.GET.get('date_entretien', '').strip()

    entretiens = Entretien.objects.all()

    # Search logic
    if candidat_query:
        entretiens = entretiens.filter(candidature__nom_candidat__icontains=candidat_query)
    if statut_query:
        entretiens = entretiens.filter(statut_entretien__iexact=statut_query)
    
    # Handle date filtering if provided
    if date_entretien_query:
        try:
            # Convert string to date format
            date_entretien = datetime.strptime(date_entretien_query, '%Y-%m-%d').date()
            entretiens = entretiens.filter(date_entretien=date_entretien)
        except ValueError:
            pass

    # Build the Entretien data for rendering
    entretiens_data = []
    for entretien in entretiens:
        entretiens_data.append({
            'id': entretien.id_entretien,
            'candidat': entretien.id_candidature.nom_candidat,
            'date_entretien': entretien.date_entretien,
            'heure': entretien.date_entretien.strftime('%H:%M'),
            'lieu': entretien.lieu_entretien,
            'statut': entretien.statut_entretien,
        })
    
    print(entretiens_data)

    return render(request, 'entretien/liste_entretiens.html', {'entretiens': entretiens_data
                                                               , 'current_url': request.path.lstrip('/')})

@login_required
def consulter_entretien(request, entretien):
    fetched_entretien = get_object_or_404(Entretien, id_entretien=entretien)
    
    entretien_info = {
        'id_entretien': fetched_entretien.id_entretien,
        'candidat': fetched_entretien.id_candidature.nom_candidat,
        'date_entretien': fetched_entretien.date_entretien,
        'heure': fetched_entretien.date_entretien.strftime('%H:%M'),
        'lieu': fetched_entretien.lieu_entretien,
        'statut': fetched_entretien.statut_entretien,
    }
    
    print(entretien_info)
    
    return render(request, 'entretien/consulter_entretien.html', {'entretien': entretien_info
                                                                  , 'current_url': request.path.lstrip('/')})

@login_required
def ajouter_entretien(request):
    if request.method == 'POST':
        id_candidature = request.POST.get('id_candidature')
        date_entretien = request.POST.get('date_entretien')  # format: YYYY-MM-DD
        heure_entretien = request.POST.get('heure_entretien')  # format: HH:MM

        # Validate required fields
        if not id_candidature or not date_entretien or not heure_entretien:
            messages.error(request, _("Tous les champs obligatoires doivent être remplis."))
            return redirect('ajouter_entretien')

        try:
            candidature = Candidature.objects.get(id_candidature=id_candidature)

            # Merge date and time into a single datetime object
            # Assume 'date_entretien' is in YYYY-MM-DD format and 'heure_entretien' is in HH:MM format
            full_datetime_str = f"{date_entretien} {heure_entretien}"  # Merge date and time string
            full_datetime = datetime.strptime(full_datetime_str, "%Y-%m-%d %H:%M")  # Convert to datetime object

            # Create new entretien (interview) with the combined datetime
            entretien = Entretien.objects.create(
                id_candidature=candidature,
                date_entretien=full_datetime,  # Save as a datetime object
                lieu_entretien=request.POST.get('lieu_entretien'),
                statut_entretien=request.POST.get('statut_entretien'),
                notes=request.POST.get('notes_entretien')
            )

            messages.success(request, _("L'entretien a été planifié avec succès."))
            return redirect('/entretien/liste_entretiens')

        except Candidature.DoesNotExist:
            messages.error(request, _("La candidature sélectionnée n'existe pas."))
            return redirect('ajouter_entretien')

    # Get the list of candidatures to select from
    candidatures = Candidature.objects.all()
    return render(request, 'entretien/ajouter_entretien.html', {'candidatures': candidatures
                                                                , 'current_url': request.path.lstrip('/')})

@login_required
def modifier_entretien(request, entretien):
    entretien_instance = get_object_or_404(Entretien, id_entretien=entretien)

    if request.method == 'POST':
        entretien_instance.date_entretien = request.POST.get('date_entretien')
        entretien_instance.heure_entretien = request.POST.get('heure_entretien')
        entretien_instance.lieu_entretien = request.POST.get('lieu_entretien')
        entretien_instance.statut_entretien = request.POST.get('statut_entretien')

        # Validate required fields
        if not entretien_instance.date_entretien or not entretien_instance.heure_entretien or not entretien_instance.lieu_entretien or not entretien_instance.statut_entretien:
            return render(request, 'entretien/modifier_entretien.html', {
                'entretien': entretien_instance,
                'error_message': _('Tous les champs sont obligatoires.')
            })

        try:
            entretien_instance.save()
            return redirect('/Entretien/liste_entretiens')
        except Exception as e:
            return render(request, 'entretien/modifier_entretien.html', {
                'entretien': entretien_instance,
                'error_message': _('Une erreur s\'est produite lors de la modification.'),
                'exception': str(e)
            })

    return render(request, 'entretien/modifier_entretien.html', {'entretien': entretien_instance
                                                                 , 'current_url': request.path.lstrip('/')})

@login_required
def supprimer_entretien(request, entretien):
    entretien_instance = get_object_or_404(Entretien, id_entretien=entretien)

    if request.method == 'POST':
        try:
            entretien_instance.delete()
            return redirect('liste_entretien')
        except Exception as e:
            return render(request, 'entretien/supprimer_entretien.html', {
                'entretien': entretien_instance,
                'error_message': _('Une erreur s\'est produite lors de la suppression.'),
                'exception': str(e)
            })

    return render(request, 'entretien/supprimer_entretien.html', {'entretien': entretien_instance
                                                                  , 'current_url': request.path.lstrip('/')})