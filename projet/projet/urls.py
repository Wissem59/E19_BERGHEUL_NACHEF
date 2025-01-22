from django.contrib import admin
from django.urls import path
from salaire import views as salaire_views
from contrats import views as contrats_views
from salaire import tasks as salaire_tasks
from app import views as app_views 
from recrutement import views as recrutement_views
from dashboard import views as dashboard_views
from authentification import views as authentification_views
from favoris import views as favoris_views
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static


from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('personnels/', include('app.urls')),
    
    path('Pointage/ajouter', salaire_views.ajouter_absence, name='ajouter_absence'), 
    path('Pointage/modifier/<int:employe>/<str:date>', salaire_views.modifier_absence, name='modifier_absence'), 
    path('Pointage/liste_assiduite', salaire_views.Personnel_assiduite, name='employe_assiduite'), 
   
    path('Salaire/liste_salaires', salaire_views.employee, name='salaire'),
    path('Salaire/modifier/<int:employe>/<str:date>', salaire_views.modifier_salaire, name='modifier_salaire'),
    path('Salaire/Fiche_de_paie/<int:employe>/<str:date>', salaire_views.ajouter_fiche_paie, name='ajouter_fiche_paie'),
    path('Salaire/Prendre_massrouf/<int:employe>/<str:date>', salaire_views.prendre_massrouf, name='prendre_massrouf'),

    path('Contrat/liste_contrats', contrats_views.liste_contrats, name='liste_contrats'),
    path('Contrat/archive_contrats', contrats_views.archive_contrats, name='archive_contrats'), 
    path('Contrat/ajouter', contrats_views.ajouter_contrat, name='ajouter_contrat'), 
    path('Contrat/supprimer/<int:contrat_id>', contrats_views.supprimer_contrat, name='supprimer_contrat'), 
    path('Contrat/modifier/<int:contrat_id>', contrats_views.modifier_contrat, name='modifier_contrat'), 
    path('Contrat/consulter/<int:contrat_id>', contrats_views.consulter_contrat, name='consulter_contrat'), 
    path('Contrat/renouveler/<int:contrat_id>', contrats_views.renouveler_contrat, name='renouveler_contrat'), 
    path('Contrat/terminer/<int:contrat_id>', contrats_views.terminer_contrat, name='terminer_contrat'), 
    path('Contrat/suivi_periode_dessai', contrats_views.suivi_periode_dessai, name='suivi_periode_dessai'), 
    
    path('Offre_emploi/liste_offres_emploi', recrutement_views.liste_offres_emploi, name='liste_offre_emploi'), 
    path('Offre_emploi/publier', recrutement_views.publier_offre_emploi, name='publier_offre_emploi'), 
    path('Offre_emploi/consulter/<int:offre_emploi>', recrutement_views.consulter_offre_emploi, name='consulter_offre_emploi'),
    path('Offre_emploi/modifier/<int:offre_emploi>', recrutement_views.modifier_offre_emploi, name='modifier_offre_emploi'),
    path('Offre_emploi/supprimer/<int:offre_emploi>', recrutement_views.supprimer_offre_emploi, name='supprimer_offre_emploi'), 
    
    path('Condidature/liste_candidats', recrutement_views.liste_candidats, name='liste_candidats'), 
    path('Condidature/soumettre_candidature', recrutement_views.soumettre_candidature, name='soumettre_candidature'), 
    path('Condidature/modifier/<int:candidature>', recrutement_views.modifier_statut_candidature, name='modifier_statut_candidature'),
    path('Condidature/consulter/<int:candidature>', recrutement_views.consulter_candidature, name='consulter_candidature'), 
    
    path('Entretien/liste_entretiens', recrutement_views.liste_entretiens, name='liste_entretiens'), 
    path('Entretien/ajouter', recrutement_views.ajouter_entretien, name='ajouter_entretien'), 
    path('Entretien/consulter/<int:entretien>', recrutement_views.consulter_entretien, name='consulter_entretien'),
    path('Entretien/modifier/<int:entretien>', recrutement_views.modifier_entretien, name='modifier_entretien'),
    path('Entretien/supprimer/<int:entretien>', recrutement_views.supprimer_entretien, name='supprimer_entretien'), 
    
    path('Dashboard', dashboard_views.dashboard, name='dashboard'), 

    path('login/', authentification_views.login_view, name='login'),
    path('signup/', authentification_views.signup_view, name='signup'),
    path('logout/', authentification_views.logout_view, name='logout'),

    #favoris urls
    path('home/', favoris_views.liste_favoris, name='liste_favoris'),
    path('ajouter_favori/<path:current_url>', favoris_views.ajouter_favori, name='ajouter_favoris'),
    path('Favoris/supprimer_favoris/<int:section_id>/', favoris_views.supprimer_favoris, name='supprimer_favoris'),

    path('store-urls/', favoris_views.store_urls_in_sections, name='store_urls_in_sections'),

    path('favicon.ico', serve, {'path': 'favicon.ico', 'document_root': settings.STATIC_ROOT}),


] + static('/projet/projet/js/', document_root=settings.BASE_DIR / 'projet/projet/js')
