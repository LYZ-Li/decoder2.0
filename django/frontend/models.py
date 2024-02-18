from django.db import models

# Create your models here.
class ServiceStatus(models.Model):
    name = models.CharField(max_length=100)
    is_running = models.BooleanField(default=False)
