from django.urls import path
from . import views

urlpatterns = [
    path('api/github-wrapped/', views.generate_github_wrapped, name='github-wrapped'),
]