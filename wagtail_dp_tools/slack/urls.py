# slack/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('show-text/', views.SlackPageView.as_view(), name='slack_admin'),  # URL para la vista show_text
]