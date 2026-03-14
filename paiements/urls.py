from django.urls import path
from . import views

urlpatterns = [
    path('<int:reservation_pk>/', views.paiement, name='paiement'),
    path('confirmation/<int:pk>/', views.paiement_confirmation, name='paiement_confirmation'),
    path('historique/', views.historique_paiements, name='historique_paiements'),
    path('<int:pk>/recu/', views.telecharger_recu, name='telecharger_recu'),
]