from django.urls import path
from . import views

urlpatterns = [
    path("", views.btech_skills, name="btech_skills"),
    path("branch/", views.btech_branch, name="btech_branch"),
    path("view-all/", views.btech_view_all, name="btech_view_all"),
    path("course/", views.course_detail, name="course_detail"),
]
