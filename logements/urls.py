from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='logements_list'),
    path('search/', views.logement_search, name='logements_search'),
    path('mes-logements/', views.mes_logements, name='mes_logements'),
    path('ajouter/', views.logement_create, name='logement_create'),
    path('<int:pk>/', views.logement_detail, name='logement_detail'),
    path('<int:pk>/modifier/', views.logement_edit, name='logement_edit'),
    path('<int:pk>/supprimer/', views.logement_delete, name='logement_delete'),
    path('temoignage/', views.ajouter_temoignage, name='ajouter_temoignage'),
    path('<int:pk>/avis/', views.ajouter_avis, name='ajouter_avis'),
    path('avis/<int:pk>/modifier/', views.modifier_avis, name='modifier_avis'),
    path('avis/<int:pk>/supprimer/', views.supprimer_avis, name='supprimer_avis'),
    path('mes-avis/', views.mes_avis_recus, name='mes_avis_recus'),
]