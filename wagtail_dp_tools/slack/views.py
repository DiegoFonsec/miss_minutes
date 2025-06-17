# slack/views.py
from django.http import HttpResponse

# Vista básica que muestra un texto plano
def show_text(request):
    return HttpResponse("¡Bienvenido a la aplicación Slack de Wagtail!")