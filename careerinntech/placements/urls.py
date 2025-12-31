from django.urls import path
from .views import placement_preparation

urlpatterns = [
    path("", placement_preparation, name="placement_preparation"),
]
