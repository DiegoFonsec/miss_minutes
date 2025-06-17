#urls.py
from django.urls import path, include
from wagtail_dp_tools.csrgenerator.views import csrgenerator_admin_view


urlpatterns = [
    # wagtail admin
    path('', csrgenerator_admin_view, name='csrgenerator_admin'),
    # api
    path('api/', include('wagtail_dp_tools.csrgenerator.api.urls')),
]