from core.models import Manager

def hotel_info(request):
    context = {}
    if request.user.is_authenticated:
        try:
            manager = getattr(request.user, 'manager', None)
            if manager:
                context['hotel'] = manager.hotel_post
        except Manager.DoesNotExist:
            pass
    return context