from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.forms.models import model_to_dict
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from datetime import date, datetime
from .models import Salaire, Presence, Massrouf
from app.models import Personnel
from .forms import AjouterAbsenceForm, ModifierAbsenceForm
from decimal import Decimal
from django.contrib.auth.decorators import login_required

@login_required
def today_date(request):
    """
    Display today's date on the attendance page.
    """
    return render(request, 'system_de_pointage.html', {'today': date.today(), 
                                                       'current_url': request.path.lstrip('/')})

def ajouter_absences(personnel, absence_date=None, state=True):
    """
    Add an absence record and update the salary absences count.

    Args:
        personnel (int | Personnel): Employee's ID or Personnel instance.
        absence_date (date | None): The date of absence (default: today).
        state (bool): Whether the employee was absent (default: True).
    """
    absence_date = absence_date or date.today()

    # Ensure 'personnel' is a Personnel instance
    personnel = get_object_or_404(Personnel, id=personnel) if isinstance(personnel, int) else personnel

    # Create or update a Presence record
    presence = Presence.objects.create(date_absence=absence_date, is_absent=state)
    presence.id_employe.set([personnel])

    if state:
        salaire, created = Salaire.objects.get_or_create(
            id_employe=personnel,
            date_paie__year=absence_date.year,
            date_paie__month=absence_date.month,
            defaults={"montant": calculer_salaire(personnel, absence_date), "absences": 0}
        )
        salaire.absences += 3 if absence_date.weekday() == 3 else 1
        salaire.save()

def reset_massrouf_annuel():
    """
    Reset the annual allowance at the beginning of the year.
    """
    if date.today().month == 1 and date.today().day == 1:
        Salaire.objects.update(massrouf_annuel=0)

def reset_massrouf_mensuel():
    """
    Reset the monthly allowance at the beginning of each month.
    """
    if date.today().day == 1:
        Salaire.objects.update(massrouf_mensuel=0)

def calculer_salaire(personnel, salaire_date):
    """
    Calculate and update an employee's salary based on absences and bonuses.

    Args:
        personnel (Personnel): Employee instance.
        salaire_date (date): Date of the salary record.

    Returns:
        float: Updated salary amount.
    """
    salaire = get_object_or_404(Salaire, id_employe=personnel, date_paie=salaire_date)
    salaire.montant = (
        salaire.salaire_base -
        (salaire.absences * salaire.salaire_jour) -
        salaire.massrouf_mensuel +
        salaire.prime_total
    )
    salaire.massrouf_mensuel = 0
    salaire.save()
    return salaire.montant

@login_required
def prendre_massrouf(request, employe, date):
    """
    Handle the process of taking an advance for an employee.
    """
    # Get the employee (personnel) object
    personnel = get_object_or_404(Personnel, id=employe)

    # Convert the date string to a datetime object
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "La date fournie n'est pas valide.")
        return redirect('/Salaire/liste_salaires')

    # Get the salary (salaire) for the given employee and date
    salaire = Salaire.objects.filter(id_employe=personnel, date_paie=date_obj).first()

    if not salaire:
        messages.error(request, "Aucun salaire trouvé pour cet employé et cette date.")
        return redirect('/Salaire/liste_salaires')  # Redirect if no salary is found
    
    # Get or create the massrouf for the given employee and year
    massrouf, created = Massrouf.objects.get_or_create(
        id_employe=personnel,
        annee=date_obj.year
    )
    
    # Handle form submission via POST request
    if request.method == 'POST':
        amount = request.POST.get('amount')

        if amount:
            # Check if the amount is a valid number
            try:
                avance_montant = Decimal(amount)  # Convert to Decimal here
            except ValueError:
                messages.error(request, "Le montant fourni n'est pas valide.")
                return redirect('prendre_massrouf', employe=employe, date=date)
            
            # Check if the massrouf limit is exceeded
            if massrouf.massrouf_fois >= 2:
                messages.error(request, "Le limite d'avance a été dépassée.")
                return redirect('prendre_massrouf', employe=employe, date=date)
            
            # Increment the massrouf_fois and update the massrouf amount
            massrouf.massrouf_fois += 1
            massrouf.montant = massrouf.montant + avance_montant  # Ensure both are Decimal
            
            # Update the salary details
            salaire.massrouf_mensuel = salaire.massrouf_mensuel + avance_montant  # Ensure both are Decimal
            salaire.save()
            massrouf.save()

            # Provide feedback to the user
            if created:
                messages.success(request, "Un nouveau massrouf a été créé avec succès.")
            else:
                messages.success(request, "Le massrouf a été mis à jour avec succès.")
            
            return redirect('/Salaire/liste_salaires')  # Redirect after successful operation

    # Prepare the context data for rendering the form
    info = {
        'matricule': personnel.id,
        'nom': personnel.name,
        'date_paie': date_obj,
    }
    
    return render(request, 'salaire/prendre_massrouf.html', {'info': info, 'current_url': request.path.lstrip('/')})

@login_required
def modifier_salaire(request, employe, date):
    """
    View to modify an employee's salary for a specific month.

    Args:
        request: Django HTTP request.
        employe (int): Employee ID.
        salaire_date (date): Date of the salary record.
    """
    personnel = get_object_or_404(Personnel, id=employe)
    salaire = get_object_or_404(Salaire, id_employe=employe, date_paie=date)

    if request.method == "POST":
        try:
            # Update salary details
            salaire.salaire_base = float(request.POST.get("salaire_base", salaire.salaire_base))
            salaire.salaire_jour = float(request.POST.get("salaire_jour", salaire.salaire_jour))
            salaire.absences = int(request.POST.get("absences", salaire.absences))
            salaire.massrouf_mensuel = float(request.POST.get("massrouf_mensuel", salaire.massrouf_mensuel))
            salaire.prime_performance = float(request.POST.get("prime_performance", salaire.prime_performance))
            salaire.prime_festive = float(request.POST.get("prime_festive", salaire.prime_festive))
            salaire.save()

            messages.success(request, f"Salaire mis à jour avec succès pour {personnel.name} ({salaire.date_paie}).")
            return redirect("/Salaire/liste_salaires")
        except (ValueError, ValidationError) as e:
            messages.error(request, f"Erreur de mise à jour: {str(e)}")

    return render(request, "salaire/modifier_salaire.html", {"personnel": model_to_dict(personnel),
        "salaire": model_to_dict(salaire), 
                                                                   'current_url': request.path.lstrip('/')})

@login_required
def employee(request):
    # Queryset for salaries
    salaire_queryset = Salaire.objects.all()

    # Extract GET parameters
    id_employe = request.GET.get('id_employe', '')
    query_date = request.GET.get('q', '')  # Match the input name in your template

    print(query_date)
    
    # Filter by employee ID
    if id_employe:
        salaire_queryset = salaire_queryset.filter(id_employe_id=id_employe)

    # Filter by month and year
    if query_date:
        try:
            # Parse query_date as a date object (format: YYYY-MM)
            year, month = map(int, query_date.split('-'))
            current_date = datetime.now()

            # Validate the date to ensure it's not in the future
            if year > current_date.year or (year == current_date.year and month > current_date.month):
                messages.error(request, "La date saisie est dans le futur. Veuillez sélectionner une date valide.")
            else:
                # Apply filters for the year and month
                salaire_queryset = salaire_queryset.filter(
                    date_paie__year=year,
                    date_paie__month=month
                )
        except ValueError:
            messages.error(request, "Format de date invalide. Utilisez le format YYYY-MM.")

    # Attach employee details to each salary
    employe_salaire = []
    for salaire_instance in salaire_queryset.select_related('id_employe'):
        personnel = salaire_instance.id_employe
        if personnel:
            employe_salaire.append({
                **model_to_dict(personnel),
                'salaire': model_to_dict(salaire_instance),
                'date_paie': salaire_instance.date_paie.strftime('%Y-%m-%d'),
            })

    # Default value for the date input
    current_date = datetime.now()
    default_month_year = f"{current_date.year}-{current_date.month:02d}"

    # Context for rendering
    context = {
        'employe_salaire': employe_salaire,
        'current_url': request.path.lstrip('/'),
        'default_month_year': default_month_year,
    }
    return render(request, 'salaire/liste_salaire.html', context)




@login_required
def Personnel_assiduite(request):
    # Retrieve search parameters from the GET request
    id_employe_query = request.GET.get('id_employe', '').strip()
    nom_employe_query = request.GET.get('nom_employe', '').strip()
    date_query = request.GET.get('q', '').strip()

    # Default to today's date if no date is provided
    if not date_query:
        date_query = now().date()

    # Filter Presence objects based on search parameters
    assiduite = Presence.objects.all()

    if id_employe_query:
        assiduite = assiduite.filter(id_employe__id__icontains=id_employe_query)
    if nom_employe_query:
        assiduite = assiduite.filter(id_employe__name__icontains=nom_employe_query)
    if date_query:
        assiduite = assiduite.filter(date_absence=date_query)

    # Get or create Presence instances for today for each employee
    for personnel in Personnel.objects.all():
        # Try to get the Presence for today, if not exists, create one with default `is_absent=True`
        presence, created = Presence.objects.get_or_create(
            id_employe=personnel,
            date_absence=date_query,
            defaults={'is_absent': True}  # Set default as True, assuming employee is absent by default
        ) 
    
    # Build the assiduite data for rendering
    assiduite_data = []
    for presence in assiduite:
        personnel = presence.id_employe  # Get the related Personnel instance
        assiduite_data.append({
            'matricule': personnel.id,
            'nom': personnel.name,
            'is_absent': 'Absent' if presence.is_absent else 'Present',
            'date_absence': presence.date_absence,
        })

    # Pass the filtered data and today's date to the template
    context = {
        'assiduite': assiduite_data,
        'today_date': now().strftime('%Y-%m-%d'),  # Format date for input type="date"
        'current_url': request.path.lstrip('/')
    }

    return render(request, 'absences/liste_absences.html', context)

@login_required
def ajouter_absence(request):
    """
    View to add an absence record.
    """
    if request.method == 'POST':
        form = AjouterAbsenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Absence ajoutée avec succès.")
            return redirect('ajouter_absence')
        messages.error(request, "Erreur lors de l'ajout de l'absence.")
    else:
        form = AjouterAbsenceForm()
    return render(request, "absences/ajouter_absence.html", {"form": form,'current_url': request.path.lstrip('/')})

@login_required
def ajouter_fiche_paie(request, employe, date):
    """
    View to generate and display a salary slip.
    """
    calculer_salaire(employe, date)
    salaire = get_object_or_404(Salaire, id_employe=employe, date_paie=date)
    personnel = get_object_or_404(Personnel, id=employe)
    fiche_paie = {**model_to_dict(salaire), **model_to_dict(personnel)}
    return render(request, 'salaire/fiche_paie.html', {'fiche_paie': fiche_paie, 'current_url': request.path.lstrip('/')})

def assign_primes(personnel_id, performance_bonus=0, festive_bonus=0, month_date=None):
    """
    Assign bonuses to an employee for a specific month.
    """
    month_date = month_date or date.today()
    personnel = get_object_or_404(Personnel, id=personnel_id)
    salaire, _ = Salaire.objects.get_or_create(
        id_employe=personnel,
        date_paie__year=month_date.year,
        date_paie__month=month_date.month,
        defaults={"montant": 0, "absences": 0}
    )
    salaire.prime_performance = performance_bonus
    salaire.prime_festive = festive_bonus
    salaire.save()
    return salaire

@login_required
def ajouter_prime(request):
    """
    View to add performance or festive bonuses.
    """
    if request.method == 'POST':
        personnel_id = request.POST.get('personnel_id')
        performance_bonus = float(request.POST.get('performance_bonus', 0))
        festive_bonus = float(request.POST.get('festive_bonus', 0))
        month_date = request.POST.get('month_date')
        month_date = datetime.strptime(month_date, '%Y-%m-%d').date() if month_date else None

        salaire = assign_primes(personnel_id, performance_bonus, festive_bonus, month_date)
        return render(request, 'primes/ajouter_prime.html', {'salaire': salaire})
    return render(request, 'primes/ajouter_prime.html', {'current_url': request.path.lstrip('/')})

@login_required
def modifier_absence(request, employe, date):
    try:
        # Convert the date string to a date object
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        # Handle invalid date format if needed
        return render(request, 'error_page.html', {'message': 'Invalid date format'})

    # Fetch the specific 'Presence' record using the employee ID and date
    presence = get_object_or_404(Presence, id_employe=employe, date_absence=date_obj)
    personnel = get_object_or_404(Personnel, id=employe)

    # Get the related Salaire record for the employee for the given month
    salaire = get_object_or_404(Salaire, id_employe=employe, date_paie=date_obj.replace(day=1))

    # Store the current value of is_absent before any changes
    previous_is_absent = presence.is_absent

    info = {
        "matricule": presence.id,
        "nom": personnel.name,
        "date_absence": presence.date_absence,
        "absence": presence.is_absent,
        'current_url': request.path.lstrip('/')
    }

    if request.method == 'POST':
        form = ModifierAbsenceForm(request.POST, instance=presence)  # Pre-fill the form with existing data
        if form.is_valid():
            # Save changes to the 'Presence' model
            form.save()

            # Check if the absence status has changed
            if presence.is_absent != previous_is_absent:
                if presence.is_absent:  # Changed to True (absent)
                    salaire.absences += 1
                else:  # Changed to False (present)
                    salaire.absences -= 1

                # Save the updated 'Salaire' instance
                salaire.save()

            mssg = "Assiduite modifiée avec succès."
            return render(request, "absences/modifier_absence.html", {"form": form, "message": mssg, "info": info,
                                                                      'current_url': request.path.lstrip('/')})
        else:
            mssg = "Veuillez remplir tous les champs!"
            return render(request, "absences/modifier_absence.html", {"form": form, "message": mssg, "info": info,
                                                                      'current_url': request.path.lstrip('/')})
    else:
        form = ModifierAbsenceForm(instance=presence)  # Pre-fill the form with existing data
        return render(request, "absences/modifier_absence.html", {"form": form, "info": info,
                                                                   'current_url': request.path.lstrip('/')})

@login_required
def supprimer_absence(request, absence_id):
    """
    View to delete an absence record.

    Args:
        request: Django HTTP request.
        absence_id (int): ID of the absence record.
    """
    absence = get_object_or_404(Presence, id=absence_id)
    if request.method == 'POST':
        absence.delete()
        messages.success(request, "Absence supprimée avec succès.")
        return redirect('liste_absences')
    return