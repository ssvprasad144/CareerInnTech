from django.shortcuts import render
from .data import PLACEMENT_MODULES

def placement_preparation(request):
    return render(
        request,
        "placements/placement_preparation.html",
        {"modules": PLACEMENT_MODULES},
    )
