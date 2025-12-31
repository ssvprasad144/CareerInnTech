from django.shortcuts import render
from .data import PERSONALIZED_PROJECTS

def projects(request):
    # TEMP: later take from profile
    user_track = "btech-cse"

    projects = PERSONALIZED_PROJECTS.get(user_track, [])

    return render(
        request,
        "projects/projects.html",
        {"projects": projects}
    )
