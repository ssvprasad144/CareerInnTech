from django.urls import path   # ✅ THIS LINE WAS MISSING
from .views import projects_home

urlpatterns = [
    path("", projects_home, name="projects"),
]
