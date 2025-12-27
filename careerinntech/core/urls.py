
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('welcome/', views.welcome, name='welcome'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("post-login/", views.post_login, name="post_login"),

    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('colleges/', views.college_track_select, name='college-track'),
    path('colleges/btech/', views.btech_categories, name='btech-categories'),
    path("courses/", views.course_tracks, name="course_tracks"),
    path("courses/btech/", views.btech_courses, name="btech_courses"),
 path("courses/btech/cs/", views.btech_cs, name="btech_cs"),

path("courses/btech/aiml/", views.btech_aiml, name="btech_aiml"),
 path("courses/btech/ece/", views.btech_ece, name="btech_ece"),
path("courses/btech/ee/", views.btech_ee, name="btech_ee"),
path("courses/btech/mech/", views.btech_mech, name="btech_mech"),
path("support/", views.support, name="support"),
path("dashboard/jobs/", views.jobs, name="jobs"),
path("dashboard/projects/", views.projects, name="projects"),
path("previous-papers/", views.paper_select, name="paper_select"),
path("previous-papers/btech/", views.btech_previous_year_papers, name="btech_papers"),
path("previous-papers/hospitality/", views.hospitality_previous_year_papers, name="hospitality_papers"),
path("profile/edit/", views.edit_profile, name="edit_profile"),

path("ai-chat/", views.ai_chat_page, name="ai_chat"),
    path("api/ai-chat/", views.openai_ai_chat, name="openai_ai_chat"),

]    

