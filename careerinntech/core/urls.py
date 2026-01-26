from django.urls import path, include
from . import views

urlpatterns = [

    # HOME
    path('', views.home, name='home'),

    # AUTH
    path('accounts/', include('allauth.urls')),
    path('signup/', views.otp_signup_page, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("projects/", include("projects.urls")),


    path("signup-email/", views.signup_email, name="signup_email"),
    path("verify-email/", views.verify_email, name="verify_email"),
    path("resend-email/", views.resend_email, name="resend_email"),

    path("set-password/", views.set_password, name="set_password"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),


    # POST LOGIN
    path("post-login/", views.post_login, name="post_login"),
    path('welcome/', views.welcome, name='welcome'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # PAGES
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("support/", views.support, name="support"),

    # PROFILE
    path("profile/", views.profile_page, name="profile_page"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # COLLEGES
    path('colleges/', views.college_track_select, name='college-track'),
    path('colleges/btech/', views.btech_categories, name='btech-categories'),

    path("courses/", views.course_tracks, name="course_tracks"),
    path("courses/btech/", views.btech_courses, name="btech_courses"),
    path("courses/btech/cs/", views.btech_cs, name="btech_cs"),
    path("courses/btech/aiml/", views.btech_aiml, name="btech_aiml"),
    path("courses/btech/ece/", views.btech_ece, name="btech_ece"),
    path("courses/btech/ee/", views.btech_ee, name="btech_ee"),
    path("courses/btech/mech/", views.btech_mech, name="btech_mech"),

    # PLACEMENTS
    path("placement-preparation/", views.placement_preparation, name="placement_preparation"),
    path("placement-preparation/aptitude/", views.aptitude_preparation, name="aptitude-preparation"),
    path("placement-preparation/company-dsa/", views.company_dsa, name="company-dsa"),
    path("placement-preparation/coding-assessment/", views.coding_assessment, name="coding-assessment"),
    path("placement-preparation/resume-shortlisting/", views.resume_shortlisting, name="resume-shortlisting"),
    path("placement-preparation/group-discussion/", views.group_discussion, name="group-discussion"),

    # JOBS
    path("dashboard/jobs/", views.jobs, name="jobs"),

    # PAPERS
    path("previous-papers/", views.paper_select, name="paper_select"),
    path("previous-papers/btech/", views.btech_previous_year_papers, name="btech_papers"),
    path("previous-papers/hospitality/", views.hospitality_previous_year_papers, name="hospitality_papers"),

    # AI
    path("ai-chat/", views.ai_chat_page, name="ai_chat"),
    path("api/ai-chat/", views.openai_ai_chat, name="openai_ai_chat"),
    path("reset-ai-memory/", views.reset_ai_memory, name="reset_ai_memory"),

]
