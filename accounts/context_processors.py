from .models import Notification


def notifications(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(destinataire=request.user)[:5]
        notif_count = Notification.objects.filter(
            destinataire=request.user, lue=False
        ).count()
        return {'notifs': notifs, 'notif_count': notif_count}
    return {'notifs': [], 'notif_count': 0}