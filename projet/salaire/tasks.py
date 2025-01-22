from background_task import background
from datetime import date
from .models import Presence
from app.models import Personnel
from django.shortcuts import render

@background(schedule=60) 
def compter_assiduite(request):
    Personnels = Personnel.objects.all()
    for Personnel in Personnels:
        new_entry = Presence.objects.create(
            date_absence = date.today(),
            id = Personnel.id
            )
        Presence.save()
    return render(request, 'liste_absences.html', {'Assiduite': new_entry})



