from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def register_csrgenerator_permissions():
    content_type, created = ContentType.objects.get_or_create(
        app_label='wagtail_dp_tools.csrgenerator',  # Asegúrate de que coincida con el app_label de tu aplicación
        model='csrgenerator',  # Puedes usar un nombre genérico si el permiso no está atado a un modelo específico
    )
    return [
        Permission(
            codename='access_csrgenerator',
            name='Can access CSR Generator',
            content_type=content_type,
        )
    ]