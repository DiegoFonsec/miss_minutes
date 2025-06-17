from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wagtail_dp_tools.slack'

    def ready(self):
        from .slack_app import run_async
        run_async()
