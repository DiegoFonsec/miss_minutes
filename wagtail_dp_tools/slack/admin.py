from django.contrib import admin
from .models import SlackConfiguration

class SlackConfigurationAdmin(admin.ModelAdmin):
    list_display = ('bot_token', 'ia_token', 'bot_status')
    search_fields = ('bot_token', 'ia_token')