from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/users/', views.dashboard_users, name='dashboard_users'),
    path('dashboard/users/<int:pk>/toggle/', views.dashboard_toggle_user, name='dashboard_toggle_user'),
    path('dashboard/users/<int:pk>/role/', views.dashboard_change_role, name='dashboard_change_role'),
    path('dashboard/logements/', views.dashboard_logements, name='dashboard_logements'),
    path('dashboard/reservations/', views.dashboard_reservations, name='dashboard_reservations'),
    path('dashboard/paiements/', views.dashboard_paiements, name='dashboard_paiements'),
    path('dashboard/temoignages/', views.dashboard_temoignages, name='dashboard_temoignages'),
path('dashboard/temoignages/<int:pk>/approuver/', views.dashboard_approuver_temoignage, name='dashboard_approuver_temoignage'),
path('dashboard/temoignages/<int:pk>/rejeter/', views.dashboard_rejeter_temoignage, name='dashboard_rejeter_temoignage'),
path('dashboard/logements/<int:pk>/toggle/', views.dashboard_toggle_logement, name='dashboard_toggle_logement'),
path('notification/<int:pk>/lue/', views.marquer_notif_lue, name='marquer_notif_lue'),
]