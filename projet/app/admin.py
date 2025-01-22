from django.contrib import admin

from .models import Conge, Evaluation, Personnel, Service

# Register your models here.

admin.site.register(Personnel) 
admin.site.register(Service) 
admin.site.register(Evaluation)
admin.site.register(Conge)






