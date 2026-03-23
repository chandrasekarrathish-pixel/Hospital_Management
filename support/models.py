from django.db import models


class SupportMessage(models.Model):
    sender_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    is_emergency = models.BooleanField(default=False, help_text="Check if this is a medical emergency")

    # Admin or Doctor can leave a reply
    admin_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender_name} - Emergency: {self.is_emergency}"