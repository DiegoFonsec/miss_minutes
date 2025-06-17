#apps.py
from django.apps import AppConfig

class WagtailQaToolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wagtail_dp_tools.csrgenerator'
    label = 'csrgenerator'
