from .models import Transaction, Site


def navigation_context(request):
    if request.user.is_authenticated:
        selected_site_id = request.COOKIES.get('selectedSite')

        if selected_site_id and selected_site_id != 'ALL':
            pending_confirmations = Transaction.objects.filter(
                type=Transaction.Type.TRANSFER,
                status=Transaction.Status.PENDING,
                dest_site=selected_site_id
            )
        else:
            pending_confirmations = Transaction.objects.filter(
                type=Transaction.Type.TRANSFER,
                status=Transaction.Status.PENDING
            )

        return {
            'pending_confirmations': pending_confirmations,
            'pending_confirmations_count': pending_confirmations.count(),
            'sites': Site.objects.filter(obsoleted=False),
            'current_site': selected_site_id,
        }
    return {}
