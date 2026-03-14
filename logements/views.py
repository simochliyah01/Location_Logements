from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Logement, Temoignage
from .forms import LogementForm
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    logements = Logement.objects.filter(disponible=True)
    return render(request, 'logements/home.html', {'logements': logements})

@login_required
def logement_detail(request, pk):
    logement = get_object_or_404(Logement, pk=pk)
    return render(request, 'logements/detail.html', {'logement': logement})

@login_required
def logement_search(request):
    logements = Logement.objects.filter(disponible=True)
    ville = request.GET.get('ville', '')
    prix_max = request.GET.get('prix_max', '')
    if ville:
        logements = logements.filter(ville__icontains=ville)
    if prix_max:
        logements = logements.filter(prix_par_nuit__lte=prix_max)
    return render(request, 'logements/search.html', {'logements': logements})

@login_required
def logement_create(request):
    if not request.user.is_proprietaire():
        messages.error(request, "Seuls les propriétaires peuvent ajouter des logements.")
        return redirect('logements_list')
    if request.method == 'POST':
        form = LogementForm(request.POST, request.FILES)
        if form.is_valid():
            logement = form.save(commit=False)
            logement.proprietaire = request.user
            logement.save()
            messages.success(request, "Logement ajouté avec succès !")
            return redirect('logement_detail', pk=logement.pk)
    else:
        form = LogementForm()
    return render(request, 'logements/form.html', {'form': form, 'titre': 'Ajouter un logement'})

@login_required
def logement_edit(request, pk):
    logement = get_object_or_404(Logement, pk=pk)
    if logement.proprietaire != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce logement.")
        return redirect('logements_list')
    if request.method == 'POST':
        form = LogementForm(request.POST, request.FILES, instance=logement)
        if form.is_valid():
            form.save()
            messages.success(request, "Logement modifié avec succès !")
            return redirect('logement_detail', pk=logement.pk)
    else:
        form = LogementForm(instance=logement)
    return render(request, 'logements/form.html', {'form': form, 'titre': 'Modifier le logement'})

def logement_detail(request, pk):
    from .models import Avis
    from django.db.models import Avg
    logement = get_object_or_404(Logement, pk=pk)
    avis = Avis.objects.filter(logement=logement)
    moyenne = avis.aggregate(Avg('note'))['note__avg']
    
    # Vérifier si le user peut laisser un avis
    peut_noter = False
    a_deja_note = False
    if request.user.is_authenticated and hasattr(request.user, 'is_locataire') and request.user.is_locataire():
        from reservations.models import Reservation
        peut_noter = Reservation.objects.filter(
            logement=logement,
            locataire=request.user,
            statut='confirmee'
        ).exists()
        a_deja_note = Avis.objects.filter(logement=logement, auteur=request.user).exists()

    return render(request, 'logements/detail.html', {
        'logement': logement,
        'avis': avis,
        'moyenne': moyenne,
        'peut_noter': peut_noter,
        'a_deja_note': a_deja_note,
    })

@login_required
def mes_logements(request):
    logements = Logement.objects.filter(proprietaire=request.user)
    return render(request, 'logements/mes_logements.html', {'logements': logements})


def landing(request):
    if request.user.is_authenticated:
        return redirect('logements_list')
    from accounts.models import User
    from reservations.models import Reservation
    from paiements.models import Paiement
    from django.db.models import Count

    logements = Logement.objects.filter(disponible=True)[:6]
    temoignages = Temoignage.objects.filter(approuve=True)[:3]

    # Villes dynamiques avec comptage
    from django.db.models import Count
    villes = (Logement.objects
              .filter(disponible=True)
              .values('ville')
              .annotate(total=Count('id'))
              .order_by('-total')[:5])

    # Stats dynamiques
    stats = {
        'total_users': User.objects.count(),
        'total_logements': Logement.objects.count(),
        'total_villes': Logement.objects.values('ville').distinct().count(),
        'total_reservations': Reservation.objects.count(),
    }

    return render(request, 'logements/landing.html', {
        'logements': logements,
        'temoignages': temoignages,
        'villes': villes,
        'stats': stats,
    })    



@login_required
def ajouter_temoignage(request):
    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        note = int(request.POST.get('note', 5))
        if contenu and 1 <= note <= 5:
            # Un seul témoignage par utilisateur
            Temoignage.objects.update_or_create(
                auteur=request.user,
                defaults={'contenu': contenu, 'note': note, 'approuve': True}
            )
            messages.success(request, 'Votre avis a été soumis et publié avec succès.')
        return redirect('logements_list')
    return redirect('logements_list')

@login_required
def ajouter_avis(request, pk):
    from .models import Logement, Avis
    from reservations.models import Reservation
    logement = get_object_or_404(Logement, pk=pk)

    # Vérifier que le locataire a séjourné ici
    a_sejourne = Reservation.objects.filter(
        logement=logement,
        locataire=request.user,
        statut='confirmee'
    ).exists()

    if not a_sejourne:
        messages.error(request, 'Vous devez avoir séjourné dans ce logement pour laisser un avis.')
        return redirect('logement_detail', pk=pk)

    # Vérifier qu'il n'a pas déjà laissé un avis
    if Avis.objects.filter(logement=logement, auteur=request.user).exists():
        messages.error(request, 'Vous avez déjà laissé un avis pour ce logement.')
        return redirect('logement_detail', pk=pk)

    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire', '').strip()
        if note and commentaire:
            Avis.objects.create(
                logement=logement,
                auteur=request.user,
                note=int(note),
                commentaire=commentaire
            )

            # Notification au propriétaire
            from accounts.models import Notification
            etoiles = '★' * int(note) + '☆' * (5 - int(note))
            Notification.objects.create(
                destinataire=logement.proprietaire,
                titre=f"Nouvel avis — {logement.titre}",
                message=f"{request.user.get_full_name() or request.user.username} a laissé un avis {etoiles} : \"{commentaire[:80]}{'...' if len(commentaire) > 80 else ''}\"",
                type_notif='info',
                url=f'/logements/{logement.pk}/',
                icon='fas fa-star',
                color='rgba(245,158,11,0.4)',
            )
            messages.success(request, 'Votre avis a été publié !')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')

    return redirect('logement_detail', pk=pk)

@login_required
def logement_delete(request, pk):
    logement = get_object_or_404(Logement, pk=pk)
    if logement.proprietaire != request.user and request.user.role != 'admin':
        messages.error(request, 'Non autorisé.')
        return redirect('mes_logements')
    logement.delete()
    messages.success(request, 'Logement supprimé avec succès.')
    return redirect('mes_logements')

@login_required
def modifier_avis(request, pk):
    from .models import Avis
    avis = get_object_or_404(Avis, pk=pk, auteur=request.user)
    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire', '').strip()
        if note and commentaire:
            avis.note = int(note)
            avis.commentaire = commentaire
            avis.save()
            messages.success(request, 'Avis modifié avec succès !')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')
    return redirect('logement_detail', pk=avis.logement.pk)

@login_required
def supprimer_avis(request, pk):
    from .models import Avis
    avis = get_object_or_404(Avis, pk=pk, auteur=request.user)
    logement_pk = avis.logement.pk
    avis.delete()
    messages.success(request, 'Avis supprimé.')
    return redirect('logement_detail', pk=logement_pk) 

@login_required
def mes_avis_recus(request):
    from .models import Avis
    from django.db.models import Avg, Count
    if not request.user.is_proprietaire():
        return redirect('logements_list')

    # Tous les avis sur les logements du propriétaire
    avis = Avis.objects.filter(
        logement__proprietaire=request.user
    ).select_related('logement', 'auteur').order_by('-date')

    # Stats par logement
    logements_stats = Logement.objects.filter(
        proprietaire=request.user
    ).annotate(
        nb_avis=Count('avis'),
        moyenne=Avg('avis__note')
    ).filter(nb_avis__gt=0)

    # Moyenne globale
    moyenne_globale = avis.aggregate(Avg('note'))['note__avg']

    return render(request, 'logements/mes_avis_recus.html', {
        'avis': avis,
        'logements_stats': logements_stats,
        'moyenne_globale': moyenne_globale,
        'total_avis': avis.count(),
    })