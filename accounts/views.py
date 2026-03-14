from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User
from .forms import RegisterForm, LoginForm, ProfileUpdateForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('logements_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('logements_list')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name or user.username} !')
            # Redirection selon le rôle
            if user.role == 'admin':
                return redirect('dashboard')
            else:
                return redirect('logements_list')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Profil mis à jour avec succès !')
            return redirect('profile')
        else:
            # Recharger user depuis DB pour que la sidebar affiche les vraies valeurs
            from django.contrib.auth import get_user_model
            User = get_user_model()
            fresh_user = User.objects.get(pk=request.user.pk)
            messages.error(request, 'Erreur lors de la mise à jour. Vérifiez les champs.')
            return render(request, 'accounts/profile.html', {
                'form': form,
                'user': fresh_user,
            })
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form, 'user': request.user})

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('logements_list')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('logements_list')
    from logements.models import Logement, Temoignage
    from reservations.models import Reservation
    from paiements.models import Paiement
    from django.utils import timezone
    from datetime import timedelta

    stats = {
        'total_users': User.objects.count(),
        'total_logements': Logement.objects.count(),
        'total_reservations': Reservation.objects.count(),
        'total_paiements': Paiement.objects.filter(statut='paye').count(),
        'revenus': sum(p.montant for p in Paiement.objects.filter(statut='paye')),
        'logements_disponibles': Logement.objects.filter(disponible=True).count(),
        'reservations_en_attente': Reservation.objects.filter(statut='en_attente').count(),
        'reservations_confirmees': Reservation.objects.filter(statut='confirmee').count(),
        'reservations_annulees': Reservation.objects.filter(statut='annulee').count(),
        'temoignages_en_attente': Temoignage.objects.filter(approuve=False).count(),
    }

    today = timezone.now()
    mois_labels = []
    mois_data = []
    for i in range(5, -1, -1):
        mois = today - timedelta(days=i*30)
        count = Reservation.objects.filter(
            date_reservation__year=mois.year,
            date_reservation__month=mois.month
        ).count()
        mois_labels.append(mois.strftime('%b %Y'))
        mois_data.append(count)

    users = User.objects.all().order_by('-date_joined')[:5]
    reservations = Reservation.objects.all().order_by('-date_reservation')[:5]

    return render(request, 'dashboard/index.html', {
        'stats': stats,
        'users': users,
        'reservations': reservations,
        'mois_labels': mois_labels,
        'mois_data': mois_data,
    })

@login_required
def dashboard_users(request):
    if request.user.role != 'admin':
        return redirect('logements_list')
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/users.html', {'users': users})

@login_required
def dashboard_toggle_user(request, pk):
    if request.user.role != 'admin':
        return redirect('logements_list')
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        messages.success(request, f"Utilisateur {'activé' if user.is_active else 'désactivé'}.")
    return redirect('dashboard_users')

@login_required
def dashboard_change_role(request, pk):
    if request.user.role != 'admin':
        return redirect('logements_list')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['locataire', 'proprietaire', 'admin']:
            user.role = new_role
            user.save()
            messages.success(request, f"Rôle mis à jour.")
    return redirect('dashboard_users')

@login_required
def dashboard_logements(request):
    if request.user.role != 'admin':
        return redirect('logements_list')
    from logements.models import Logement
    logements = Logement.objects.all().order_by('-date_creation')
    return render(request, 'dashboard/logements.html', {'logements': logements})

@login_required
def dashboard_reservations(request):
    if request.user.role != 'admin':
        return redirect('logements_list')
    from reservations.models import Reservation
    reservations = Reservation.objects.all().order_by('-date_reservation')
    return render(request, 'dashboard/reservations.html', {'reservations': reservations})

@login_required
def dashboard_paiements(request):
    if request.user.role != 'admin':
        return redirect('logements_list')
    from paiements.models import Paiement
    paiements = Paiement.objects.all().order_by('-date_paiement')
    return render(request, 'dashboard/paiements.html', {'paiements': paiements})


@login_required
def dashboard_temoignages(request):
    if request.user.role != 'admin':
        return redirect('logements_list')
    from logements.models import Temoignage
    temoignages = Temoignage.objects.all().order_by('-date_creation')
    return render(request, 'dashboard/temoignages.html', {'temoignages': temoignages})

@login_required
def dashboard_approuver_temoignage(request, pk):
    if request.user.role != 'admin':
        return redirect('logements_list')
    from logements.models import Temoignage
    t = get_object_or_404(Temoignage, pk=pk)
    t.approuve = True
    t.save()
    messages.success(request, 'Témoignage approuvé !')
    return redirect('dashboard_temoignages')

@login_required
def dashboard_rejeter_temoignage(request, pk):
    if request.user.role != 'admin':
        return redirect('logements_list')
    from logements.models import Temoignage
    t = get_object_or_404(Temoignage, pk=pk)
    t.delete()
    messages.success(request, 'Témoignage rejeté et supprimé.')
    return redirect('dashboard_temoignages')

@login_required
def dashboard_toggle_logement(request, pk):
    if request.user.role != 'admin':
        return redirect('logements_list')
    from logements.models import Logement
    logement = get_object_or_404(Logement, pk=pk)
    logement.disponible = not logement.disponible
    logement.save()
    messages.success(request, f"Logement {'activé' if logement.disponible else 'désactivé'}.")
    return redirect('dashboard_logements')

@login_required
def marquer_notif_lue(request, pk):
    from .models import Notification
    notif = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    notif.lue = True
    notif.save()

    if notif.type_notif in ['reservation_confirmee', 'reservation_refusee']:
        from reservations.models import Reservation
        reservation = Reservation.objects.filter(
            locataire=request.user,
            statut='confirmee' if notif.type_notif == 'reservation_confirmee' else 'annulee'
        ).order_by('-date_reservation').first()
        return render(request, 'accounts/notification_message.html', {
            'notif': notif,
            'reservation': reservation,
        })


    return redirect(notif.url)