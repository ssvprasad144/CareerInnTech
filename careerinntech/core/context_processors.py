from .models import StudentProfile

def student_profile(request):
    if request.user.is_authenticated:
        try:
            return {
                "student_profile": request.user.studentprofile
            }
        except StudentProfile.DoesNotExist:
            return {
                "student_profile": None
            }
    return {}
