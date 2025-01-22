from django.core.management.base import BaseCommand
from salaire.models import Presence
from app.models import Personnel
from django.utils.timezone import now

class Command(BaseCommand):
    help = "Create daily presence records for all employees."

    def handle(self, *args, **kwargs):
        employees = Personnel.objects.all()
        today = now().date()

        for employee in employees:
            # Check if a Presence entry already exists for the employee today
            presence, created = Presence.objects.get_or_create(
                id_employe=employee,  # Use the related object instead of the ID field
                date_absence=today,
            )
            if created:  # If the Presence record is new, associate the employee
                # There's no need to use .add() unless it's a ManyToManyField
                presence.id_employe = employee
                presence.save()

        self.stdout.write(f"Presence entries created or updated for {employees.count()} employees.")
