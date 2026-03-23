from .models import Notification

def user_notifications(request):
    """
    Makes unread notifications available globally in all HTML templates.
    """
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        return {
            'notifications': unread_notifications,
            'unread_count': unread_notifications.count()
        }
    return {'notifications': [], 'unread_count': 0}