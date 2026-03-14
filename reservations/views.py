from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reservation
from .forms import ReservationForm
from logements.models import Logement
from accounts.models import Notification


@login_required
def reserver(request, pk):
    logement = get_object_or_404(Logement, pk=pk)

    if not logement.disponible:
        messages.error(request, 'Ce logement n\'est pas disponible.')
        return redirect('logement_detail', pk=pk)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.locataire = request.user
            reservation.logement = logement
            reservation.statut = 'en_attente'
            reservation.save()

            # Notif propriétaire — URL correcte
            Notification.objects.create(
                destinataire=logement.proprietaire,
                titre=f"Nouvelle réservation — {logement.titre}",
                message=f"{request.user.get_full_name() or request.user.username} souhaite réserver du {reservation.date_arrivee} au {reservation.date_depart}.",
                type_notif='nouvelle_reservation',
                url=f'/reservations/proprietaire/',
                icon='fas fa-calendar-plus',
                color='rgba(124,111,247,0.5)',
            )
            messages.success(request, 'Réservation envoyée ! En attente de confirmation du propriétaire.')
            return redirect('mes_reservations')
    else:
        form = ReservationForm()

    return render(request, 'reservations/reserver.html', {'form': form, 'logement': logement})


@login_required
def mes_reservations(request):
    reservations = Reservation.objects.filter(locataire=request.user).order_by('-date_reservation')
    return render(request, 'reservations/mes_reservations.html', {'reservations': reservations})


@login_required
def reservations_proprietaire(request):
    # Vérifie que c'est un propriétaire OU un admin
    if request.user.role not in ['proprietaire', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('logements_list')

    # Marquer notifs nouvelle_reservation comme lues
    Notification.objects.filter(
        destinataire=request.user,
        type_notif='nouvelle_reservation',
        lue=False
    ).update(lue=True)

    # Admin voit tout, propriétaire voit seulement ses logements
    if request.user.role == 'admin':
        reservations = Reservation.objects.all().order_by('-date_reservation')
    else:
        reservations = Reservation.objects.filter(
            logement__proprietaire=request.user
        ).order_by('-date_reservation')

    return render(request, 'reservations/reservations_proprietaire.html', {'reservations': reservations})

@login_required
def confirmer_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)

    if reservation.logement.proprietaire != request.user and request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('logements_list')

    reservation.statut = 'confirmee'
    reservation.save()

    proprietaire = request.user
    tel = getattr(proprietaire, 'telephone', None) or 'Non renseigné'
    nom = proprietaire.get_full_name() or proprietaire.username

    # Notif locataire — confirmation
    Notification.objects.create(
        destinataire=reservation.locataire,
        titre=f"✅ Réservation confirmée — {reservation.logement.titre}",
        message=f"""Félicitations ! Votre réservation pour "{reservation.logement.titre}" du {reservation.date_arrivee} au {reservation.date_depart} a été confirmée.

Pour toute question, contactez votre propriétaire :
👤 {nom}
📞 {tel}
📍 {reservation.logement.adresse}, {reservation.logement.ville}""",
        type_notif='reservation_confirmee',
        url='/reservations/mes-reservations/',
        icon='fas fa-check-circle',
        color='rgba(16,185,129,0.5)',
    )

    messages.success(request, f'Réservation de {reservation.locataire.username} confirmée !')
    return redirect('reservations_proprietaire')


@login_required
def refuser_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)

    if reservation.logement.proprietaire != request.user and request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('logements_list')

    reservation.statut = 'annulee'
    reservation.save()

    # Notif locataire — refus
    Notification.objects.create(
        destinataire=reservation.locataire,
        titre=f"❌ Réservation non disponible — {reservation.logement.titre}",
        message=f"""Nous sommes désolés, votre réservation pour "{reservation.logement.titre}" du {reservation.date_arrivee} au {reservation.date_depart} n'a pas pu être confirmée.

Nous vous invitons à consulter nos autres logements disponibles sur LocationMaroc.
Merci de votre confiance.""",
        type_notif='reservation_refusee',
        url='/logements/search/',
        icon='fas fa-times-circle',
        color='rgba(239,68,68,0.5)',
    )

    messages.success(request, f'Réservation refusée.')
    return redirect('reservations_proprietaire')


@login_required
def annuler_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.locataire != request.user:
        messages.error(request, 'Accès non autorisé.')
        return redirect('mes_reservations')
    reservation.statut = 'annulee'
    reservation.save()
    messages.success(request, 'Réservation annulée.')
    return redirect('mes_reservations')


@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.locataire != request.user and reservation.logement.proprietaire != request.user and request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('mes_reservations')

    # Récupérer la notif liée si confirmée ou refusée
    notif = Notification.objects.filter(
        destinataire=request.user,
        type_notif__in=['reservation_confirmee', 'reservation_refusee'],
    ).filter(titre__icontains=reservation.logement.titre).first()

    if notif and not notif.lue:
        notif.lue = True
        notif.save()

    return render(request, 'reservations/reservation_detail.html', {
        'reservation': reservation,
        'notif': notif,
    })