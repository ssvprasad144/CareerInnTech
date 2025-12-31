from .views import projects_home

urlpatterns = [
    path("", projects_home, name="projects"),
]
