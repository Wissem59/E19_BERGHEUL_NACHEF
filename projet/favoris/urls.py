# favoris/urls.py
from django.urls import path
from . import views as favoris_views

app_name = 'favoris'
urlpatterns = [
    
    path('home/', favoris_views.liste_favoris, name='liste_favoris'),
    path('Favoris/ajouter_favoris/', favoris_views.ajouter_favori, name='ajouter_favoris'),
    path('Favoris/supprimer_favoris/<int:section_id>/', favoris_views.supprimer_favoris, name='supprimer_favoris'),

]