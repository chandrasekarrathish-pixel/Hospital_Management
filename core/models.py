from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    # Allows uploading an icon for the homepage
    icon = models.ImageField(upload_to='department_icons/', null=True, blank=True)

    def __str__(self):
        return self.name