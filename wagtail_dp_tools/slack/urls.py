# slack/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('show-text/', views.show_text, name='show_text'),  # URL para la vista show_text
]