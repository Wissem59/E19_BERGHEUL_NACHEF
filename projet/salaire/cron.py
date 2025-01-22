from django_cron import CronJobBase, Schedule
from salaire.models import Presence
from app.models import Personnel
from django.utils.timezone import now

class CreatePresenceCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']  # Run daily at 8:00 AM

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'salaire.create_presence_cron'  # Unique code for the job

    def do(self):
        employees = Personnel.objects.all()
        today = now().date()

        for employee in employees:
            presence, created = Presence.objects.get_or_create(date_absence=today)
            if created:
                presence.id_employe.add(employee)
