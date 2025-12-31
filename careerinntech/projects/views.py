from django.shortcuts import render
from .data import PERSONALIZED_PROJECTS

def projects_home(request):

    # Read filters (safe defaults)
    track = request.GET.get("track", "btech-cse")
    project_type = request.GET.get("type", "personalized")

    # Get track data (must be dict)
    track_data = PERSONALIZED_PROJECTS.get(track, {})

    # If structure is correct, this is a dict
    # NOT a list
    projects = track_data if isinstance(track_data, dict) else {}

    context = {
        "projects": projects,
        "selected_track": track,
        "selected_type": project_type,
    }

    return render(request, "projects/projects.html", context)
