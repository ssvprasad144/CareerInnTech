from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import StudentProfile


# ---------- PUBLIC PAGES ----------
def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html", {
        'show_dashboard_header': False
    })


def contact(request):
    return render(request, "contact.html", {
        'show_dashboard_header': False
    })


# ---------- AUTH ----------
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {
                'error': 'Username already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect('welcome')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# ---------- DASHBOARD FLOW ----------
@login_required(login_url='login')
def dashboard(request):
    
    return render(request, 'dashboard.html')


@login_required(login_url='login')
def welcome(request):
    # If profile already exists, skip welcome page
    if StudentProfile.objects.filter(user=request.user).exists():
        return redirect('dashboard')

    if request.method == "POST":

        # Safety check (prevents double submit edge cases)
        if StudentProfile.objects.filter(user=request.user).exists():
            messages.info(request, "Profile already completed.")
            return redirect('dashboard')

        StudentProfile.objects.create(
            user=request.user,
            track=request.POST.get("track"),
            education=request.POST.get("education"),
            branch=request.POST.get("branch"),
            year=request.POST.get("year"),
            college=request.POST.get("college"),
            career_goal=request.POST.get("goal"),
            about=request.POST.get("about"),
            location=request.POST.get("location"),
            phone=request.POST.get("phone"),
        )

        # Success alert
        messages.success(request, "Registration completed successfully 🎉")

        return redirect('dashboard')

    return render(request, 'welcome.html')

# ---------- COLLEGE NAVIGATION ONLY ----------
@login_required(login_url='login')
def college_track_select(request):
    return render(request, 'colleges/track_select.html')


@login_required(login_url='login')
def btech_categories(request):
    return render(request, 'colleges/btech_categories.html')

def course_tracks(request):
    tracks = [
        {
            "id": "engineering",
            "title": "Engineering",
            "subtitle": "BTech & integrated programs",
            "enabled": True,
            "url": "btech_branches",
        },
        {
            "id": "hospitality",
            "title": "Hospitality",
            "subtitle": "Hotel Management & Tourism",
            "enabled": False,
            "url": "#",
        },
        {
            "id": "medical",
            "title": "Medical",
            "subtitle": "MBBS, BDS, allied sciences",
            "enabled": False,
            "url": "#",
        },
    ]

    return render(request, "colleges/course_tracks.html", {
        "tracks": tracks
    })
def btech_courses(request):
    return render(request, "colleges/btech_courses.html")

def btech_cs(request):
    return render(request, "colleges/btech/cs.html")

def btech_aiml(request):
    return render(request, "colleges/btech/aiml.html")

def btech_ece(request):
    return render(request, "colleges/btech/ece.html")

def btech_ee(request):
    return render(request, "colleges/btech/ee.html")

def btech_mech(request):
    return render(request, "colleges/btech/mech.html")

from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def welcome(request):
    if request.method == "POST":
        track = request.POST.get("track")
        year = request.POST.get("year")
        goal = request.POST.get("goal")

        UserProfile.objects.update_or_create(
            user=request.user,
            defaults={
                "track": track,
                "year": year,
                "goal": goal
            }
        )

        return redirect("dashboard")

    return render(request, "welcome.html")

def support(request):
    return render(request, "support.html")
def jobs(request):
    return render(request, "jobs.html")

from .models import Opportunity
def jobs(request):
    opportunities = Opportunity.objects.filter(is_active=True)
    return render(
        request,
        "jobs.html",
        {"jobs": opportunities}
    )

from .models import Project


def projects(request):
    projects = Project.objects.filter(is_active=True)
    return render(
        request,
        "projects.html",
        {"projects": projects}
    )

def paper_select(request):
    return render(request, "colleges/paper_select.html")

def btech_previous_year_papers(request):
    return render(request, "colleges/btech_previous_year_papers.html")

def hospitality_previous_year_papers(request):
    return render(request, "colleges/hospitality_previous_year_papers.html")
@login_required
def post_login(request):
    """
    Decides where the user should go after login
    """
    if StudentProfile.objects.filter(user=request.user).exists():
        return redirect("dashboard")
    return redirect("welcome")
