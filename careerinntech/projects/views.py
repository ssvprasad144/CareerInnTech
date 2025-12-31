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

    # TEMP: later replace with request.user.profile.track
    user_track = "btech-cse"

    # Fetch projects for this track
    projects_list = PERSONALIZED_PROJECTS.get(user_track, [])

    context = {
        "projects": projects_list,
        "track": user_track.replace("-", " ").upper(),
        "has_projects": bool(projects_list),
    }

    return render(
        request,
        "projects/projects.html",
        context
    )
