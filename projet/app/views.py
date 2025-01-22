from django.http import FileResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .report_utils import generate_evaluation_report
from .models import Conge, Evaluation, Personnel
from .forms import CongeForm, EvaluationForm, PersonnelForm
from datetime import date
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def main_page(request):
    return render(request, 'main/index.html', { 'current_url': request.path.lstrip('/')})

@login_required
def personnels(request):
    query = request.GET.get('q', '')  # Get the query from the GET request, default to empty string if not provided
    if query:
        # Filter the personnel based on the search query
        personnels = Personnel.objects.filter(name__icontains=query)  # Filter by name, can be expanded to other fields
    else:
        # If no query, return all personnel
        personnels = Personnel.objects.all()

    return render(request, 'employee/personnels.html', {'personnels': personnels, 'current_url': request.path.lstrip('/')})

def get_employe_age(employe):
    personnel = get_object_or_404(Personnel, id=employe)
    date_naissance = personnel.date_naissance
    
    today = date.today()
    age_days = today - date_naissance
    
    age_years = age_days.days // 365  # Using integer division for approximate years

    return age_years

# Update Personnel View
@login_required
def update_personnel(request, id):
    personnel = get_object_or_404(Personnel, id=id)
    if request.method == 'POST':
        form = PersonnelForm(request.POST, instance=personnel)
        if form.is_valid():
            form.save()
            return redirect('personnels')
    else:
        form = PersonnelForm(instance=personnel)
    return render(request, 'employee/update_personnel.html', {'form': form, 'current_url': request.path.lstrip('/')})

# Delete Personnel View
@login_required
def delete_personnel(request, id):
    personnel = get_object_or_404(Personnel, id=id)
    if request.method == 'POST':
        personnel.delete()
        return redirect('personnels')
    return render(request, 'employee/delete_personnel.html', {'personnel': personnel, 'current_url': request.path.lstrip('/')})


@login_required
def add_personnel(request):
    if request.method == 'POST':
        form = PersonnelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('personnels')  # Redirect to the personnel list after saving
    else:
        form = PersonnelForm()
    return render(request, 'employee/add_personnel.html', {'form': form, 'current_url': request.path.lstrip('/')})

@login_required
def evaluations(request, employee_id):
    employee = get_object_or_404(Personnel, id=employee_id)
    period = request.GET.get('period')
    if period:
        evaluations = Evaluation.objects.filter(employee=employee, period=period)
    else:
        evaluations = Evaluation.objects.filter(employee=employee)
    return render(request, 'evaluations/evaluations.html', {'employee': employee, 'evaluations': evaluations
                                                            , 'current_url': request.path.lstrip('/')})

@login_required
def add_evaluation(request, employee_id):
    employee = get_object_or_404(Personnel, id=employee_id)
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.employee = employee
            evaluation.save()
            return redirect('evaluations', employee_id=employee.id)
    else:
        form = EvaluationForm()
    
    return render(request, 'evaluations/add_evaluation.html', {'form': form, 'employee': employee, 
                                                               'current_url': request.path.lstrip('/')})

@login_required
def evaluation_list(request):
    evaluations = Evaluation.objects.all()

    # Filter by evaluation_type if selected
    evaluation_type = request.GET.get('evaluation_type')
    if evaluation_type:
        evaluations = evaluations.filter(evaluation_type=evaluation_type)

    # Render the filtered evaluations
    return render(request, 'evaluation_list.html', {'evaluations': evaluations,
                                                     'current_url': request.path.lstrip('/')})

@login_required
def evaluation_report(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    filename = generate_evaluation_report(evaluation)
    return FileResponse(open(filename, 'rb'), as_attachment=True, filename=filename)

@login_required
def liste_conges(request):
    conges = Conge.objects.all()
    employes = Personnel.objects.all()
    employe_data = [
        {
            'employe': employe,
            'jours_restants': Conge.calcul_jours_restants(employe)
        }
        for employe in employes
    ]
    return render(request, 'conges/liste_conges.html', {'conges': conges, 'employe_data': employe_data
                                                        , 'current_url': request.path.lstrip('/')})

@login_required
def ajouter_conge(request):
    if request.method == 'POST':
        form = CongeForm(request.POST)
        if form.is_valid():
            # Retrieve the employe object from the form
            employe = form.cleaned_data['employe_identifier']
            conge = form.save(commit=False)  # Do not save yet
            conge.employe = employe  # Set the employe
            conge.save()  # Now save with the correct employe
            return redirect('liste_conges')  # Redirect to a success page
    else:
        form = CongeForm()
    return render(request, 'conges/ajouter_conge.html', {'form': form, 'current_url': request.path.lstrip('/')})

@login_required
def modifier_conge(request, id):
    conge = get_object_or_404(Conge, id=id)
    if request.method == 'POST':
        form = CongeForm(request.POST, instance=conge)
        if form.is_valid():
            form.save()
            return redirect('liste_conges')
    else:
        form = CongeForm(instance=conge)
    return render(request, 'conges/modifier_conge.html', {'form': form, 'current_url': request.path.lstrip('/')})

@login_required
def supprimer_conge(request, id):
    conge = get_object_or_404(Conge, id=id)
    conge.delete()
    return redirect('liste_conges')

@login_required
def autocomplete_personnel(request):
    if 'term' in request.GET:
        qs = Personnel.objects.filter(name__icontains=request.GET['term'])
        names = list(qs.values_list('name', flat=True))
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)
