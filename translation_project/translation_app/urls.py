# translation_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload'),
    path('translate/', views.translate_file, name='translate'),
    path('confirmation/<int:file_id>/', views.confirmation, name='confirmation'),  # Add this line
]


