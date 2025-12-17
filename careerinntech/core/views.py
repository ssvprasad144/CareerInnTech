from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

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
    if not StudentProfile.objects.filter(user=request.user).exists():
        return redirect('welcome')

    return render(request, 'dashboard.html')


@login_required(login_url='login')
def welcome(request):
    if StudentProfile.objects.filter(user=request.user).exists():
        return redirect('dashboard')

    if request.method == "POST":
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

from django.shortcuts import render

def btech_courses(request):
    branches = [
        {
            "code": "cse",
            "title": "Computer Science & Engineering",
            "desc": "Software, systems, algorithms, core computing",
        },
        {
            "code": "aiml",
            "title": "Artificial Intelligence & Machine Learning",
            "desc": "AI systems, ML models, data intelligence",
        },
        {
            "code": "ds",
            "title": "Data Science",
            "desc": "Big data, analytics, statistics, ML",
        },
        {
            "code": "ece",
            "title": "Electronics & Communication Engineering",
            "desc": "Communication, VLSI, embedded systems",
        },
        {
            "code": "ee",
            "title": "Electrical Engineering",
            "desc": "Power systems, machines, control",
        },
        {
            "code": "me",
            "title": "Mechanical Engineering",
            "desc": "Design, manufacturing, thermal systems",
        },
        {
            "code": "ce",
            "title": "Civil Engineering",
            "desc": "Structures, construction, infrastructure",
        },
    ]

    return render(
        request,
        "colleges/btech_courses.html",
        {"branches": branches}
    )
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
