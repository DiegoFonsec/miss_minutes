#models.py
from django.db import models
from django.contrib.auth.models import User

class CSRGeneratorHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    project_name = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255)
    dns_san = models.TextField()
    ip_san = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
