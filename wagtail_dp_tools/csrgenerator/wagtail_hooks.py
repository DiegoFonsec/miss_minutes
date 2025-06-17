#wagtail_hooks.py
from wagtail import hooks
from django.urls import path
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail_dp_tools.csrgenerator.models import CSRGeneratorHistory
from wagtail_dp_tools.csrgenerator.views import csrgenerator_admin_view

@hooks.register('register_permissions')
def register_csrgenerator_permissions():
    content_type = ContentType.objects.get_for_model(CSRGeneratorHistory)
    
    return Permission.objects.filter(content_type=content_type)

@hooks.register('register_admin_urls')
def register_csrgenerator_admin_urls():
    return [
        path('csrgenerator/', csrgenerator_admin_view, name='csrgenerator_admin'),
    ]
