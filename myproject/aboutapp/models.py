from django.db import models

class About(models.Model):
    emblem = models.ImageField(upload_to='emblems/', blank=True, null=True)
    short_description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Про додаток"