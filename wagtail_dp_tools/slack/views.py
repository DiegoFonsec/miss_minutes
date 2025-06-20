from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from .models import SlackConfiguration

class SlackPageView(View):
    def get(self, request):
        # Aquí podrías cargar datos dinámicamente, pero por ahora solo renderizamos la plantilla
        plugin = {
            'name': 'Slack Bot',
            'description': 'Plugin para gestionar Slack'
        }
        return render(request, 'slack/admin/slack_page.html', {
            'plugin': plugin
        })
    
    def post(self, request):
        # Obtener los valores de tokens y estado
        bot_status = request.POST.get('bot_status', 'off') == 'on'
        bot_token = request.POST.get('bot_token', '')
        ia_token = request.POST.get('ia_token', '')

        # Guardamos los valores en la base de datos
        slack_config, created = SlackConfiguration.objects.update_or_create(
            id=1,  # Asumimos que solo hay una configuración
            defaults={
                'bot_token': bot_token,
                'ia_token': ia_token,
                'bot_status': bot_status
            }
        )

        # Mostrar los datos guardados
        return render(request, 'slack/admin/slack_page.html', {
            'plugin': {
                'name': 'Slack Bot',
                'description': 'Plugin para gestionar Slack'
            },
            'message': 'Configuracion guardada exitosamente.'
        })
