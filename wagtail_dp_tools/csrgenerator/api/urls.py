from django.urls import path
from wagtail_dp_tools.csrgenerator.api.views import (
    CSRGeneratorHistoryListView,
    CSRGeneratorCreateView
)

urlpatterns = [
    path('csrgenerator/<str:username>/', CSRGeneratorHistoryListView.as_view(), name='api-csrgenerator-history'),
    path('csrgenerator/', CSRGeneratorCreateView.as_view(), name='api-csrgenerator-create'),
]
