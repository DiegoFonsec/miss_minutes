
from django.db import models

class Intention(models.Model):
    machine_name = models.CharField(max_length=25)
    context = models.CharField(max_length=255)
    embedding = models.BinaryField()

    def __str__(self):
        return f'Intention: {self.machine_name} - {self.context}'

class Tone(models.Model):
    machine_name = models.CharField(max_length=25)
    context = models.CharField(max_length=255)
    embedding = models.BinaryField()

    def __str__(self):
        return f'Tone: {self.machine_name}'

# Modelo tradicional para Strike
class Strike(models.Model):
    user = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Strike: {self.user} at {self.time}'

class SlackConfiguration(models.Model):
    bot_token = models.CharField(max_length=255, help_text="Token del bot de Slack")
    ia_token = models.CharField(max_length=255, help_text="Token para el modelo de IA")
    bot_status = models.BooleanField(default=True, help_text="Estado del bot (encendido o apagado)")

    def __str__(self):
        return f"Slack Configuration: {'Active' if self.bot_status else 'Inactive'}"