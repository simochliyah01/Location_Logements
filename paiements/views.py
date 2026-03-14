from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Paiement
from reservations.models import Reservation
import uuid
from accounts.models import Notification

@login_required
def paiement(request, reservation_pk):
    reservation = get_object_or_404(Reservation, pk=reservation_pk)
    if reservation.locataire != request.user:
        messages.error(request, "Non autorisé.")
        return redirect('mes_reservations')
    # Vérifier si déjà payé
    if hasattr(reservation, 'paiement') and reservation.paiement.statut == 'paye':
        messages.info(request, "Cette réservation est déjà payée.")
        return redirect('mes_reservations')
    if request.method == 'POST':
        methode = request.POST.get('methode', 'carte')
        paiement_obj, created = Paiement.objects.get_or_create(
            reservation=reservation,
            defaults={
                'montant': reservation.prix_total,
                'methode': methode,
                'reference': str(uuid.uuid4())[:12].upper(),
                'statut': 'en_attente',
            }
        )
        if not created:
            paiement_obj.methode = methode
            paiement_obj.save()
        # Simulation : paiement toujours réussi
        paiement_obj.statut = 'paye'
        paiement_obj.save()
        reservation.statut = 'confirmee'
        reservation.save()
        Notification.objects.create(
            destinataire=reservation.logement.proprietaire,
            titre=f"Paiement reçu — {reservation.logement.titre}",
            message=f"{reservation.locataire.get_full_name() or reservation.locataire.username} a effectué le paiement de {paiement_obj.montant} DH.",
            type_notif='info',
            url=f'/paiements/{paiement_obj.pk}/recu/',
            icon='fas fa-file-pdf',
            color='rgba(16,185,129,0.5)',
        )
        messages.success(request, f"Paiement de {paiement_obj.montant} MAD effectué avec succès !")
        return redirect('paiement_confirmation', pk=paiement_obj.pk)
    return render(request, 'paiements/paiement.html', {'reservation': reservation})

@login_required
def paiement_confirmation(request, pk):
    paiement_obj = get_object_or_404(Paiement, pk=pk)
    if paiement_obj.reservation.locataire != request.user:
        return redirect('mes_reservations')
    return render(request, 'paiements/confirmation.html', {'paiement': paiement_obj})

@login_required
def historique_paiements(request):
    paiements = Paiement.objects.filter(
        reservation__locataire=request.user
    ).order_by('-date_paiement')
    return render(request, 'paiements/historique.html', {'paiements': paiements})

@login_required
def telecharger_recu(request, pk):
    from .utils import generer_recu_pdf
    from django.http import HttpResponse
    paiement = get_object_or_404(Paiement, pk=pk)

    # Vérifier accès
    if paiement.reservation.locataire != request.user and \
       paiement.reservation.logement.proprietaire != request.user and \
       request.user.role != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('logements_list')

    buffer = generer_recu_pdf(paiement)
    ref = paiement.reference if paiement.reference else str(paiement.pk).zfill(8)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_{ref}.pdf"'
    return response