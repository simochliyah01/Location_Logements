from django.urls import path
from . import views

urlpatterns = [
    path('logement/<int:pk>/', views.reserver, name='reserver'),
    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('proprietaire/', views.reservations_proprietaire, name='reservations_proprietaire'),
    path('<int:pk>/confirmer/', views.confirmer_reservation, name='confirmer_reservation'),
    path('<int:pk>/refuser/', views.refuser_reservation, name='refuser_reservation'),
    path('<int:pk>/annuler/', views.annuler_reservation, name='annuler_reservation'),
    path('<int:pk>/', views.reservation_detail, name='reservation_detail'),
]