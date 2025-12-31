from django.shortcuts import render
from .data import PERSONALIZED_PROJECTS

def projects_home(request):

    track = request.GET.get("track", "btech-cse")
    project_type = request.GET.get("type", "personalized")

    data = PERSONALIZED_PROJECTS.get(track, {})
    projects = data.get(project_type, {})

    context = {
        "track": track,
        "project_type": project_type,
        "projects": projects,
    }

    return render(request, "projects/projects.html", context)
