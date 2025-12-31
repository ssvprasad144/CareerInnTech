from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .data import PERSONALIZED_PROJECTS

@login_required(login_url="login")
def projects(request):
    """
    Personalized Projects Page
    ---------------------------
    - Uses static data (PERSONALIZED_PROJECTS)
    - Track is temporarily hardcoded
    - Later this will come from user profile
    """

    # TEMP: hardcoded (later replace with profile.track)
    user_track = "btech-cse"

    # Get projects for the track
    projects = PERSONALIZED_PROJECTS.get(user_track, [])

    context = {
        "projects": projects,
        "track": user_track.replace("-", " ").upper()
    }

    return render(request, "projects/projects.html", context)
