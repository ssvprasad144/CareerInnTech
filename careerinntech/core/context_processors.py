from .models import UserProfile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            return {"user_profile": request.user.userprofile}
        except UserProfile.DoesNotExist:
            return {"user_profile": None}
    return {}
