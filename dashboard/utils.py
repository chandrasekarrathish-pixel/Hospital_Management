from .models import Notification

def create_notification(user, message):
    """
    Utility function to generate a notification for a specific user.
    """
    Notification.objects.create(user=user, message=message)