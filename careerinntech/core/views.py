from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import StudentProfile, Opportunity, Project
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI



# ---------- PUBLIC PAGES ----------
def home(request):
    return render(request, "colleges/home.html")


def about(request):
    return render(request, "about.html", {
        "show_dashboard_header": False
    })


def contact(request):
    return render(request, "contact.html", {
        "show_dashboard_header": False
    })


# ---------- AUTH ----------
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # 1️⃣ Password mismatch
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        # 2️⃣ Username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        # 3️⃣ Email already exists (CRITICAL FIX)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")

        # 4️⃣ Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # 5️⃣ Do NOT auto-login (recommended)
        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "signup.html")



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("post_login")

        return render(request, "login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


# ---------- POST LOGIN DECISION ----------
@login_required
def post_login(request):
    """
    Decides where the user should go after login
    """
    if StudentProfile.objects.filter(user=request.user).exists():
        return redirect("dashboard")

    return redirect("welcome")


# ---------- DASHBOARD (PROTECTED) ----------
@login_required(login_url="login")
def dashboard(request):

    profile_completed = StudentProfile.objects.filter(
        user=request.user
    ).exists()

    if not profile_completed:
        messages.warning(
            request,
            "⚠️ Please complete your registration for better mentorship."
        )
        

    return render(request, "dashboard.html", {
        "profile_completed": profile_completed
    })

@login_required(login_url="login")
def edit_profile(request):

    # 🚫 If profile does NOT exist, send user to welcome page
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.warning(
            request,
            "Please complete your registration before editing your profile."
        )
        return redirect("welcome")

    if request.method == "POST":
        profile.track = request.POST.get("track")
        profile.education = request.POST.get("education")
        profile.branch = request.POST.get("branch")
        profile.year = request.POST.get("year")
        profile.college = request.POST.get("college")
        profile.university = request.POST.get("university", "")
        profile.career_goal = request.POST.get("goal")
        profile.about = request.POST.get("about")
        profile.location = request.POST.get("location")
        profile.phone = request.POST.get("phone")

        profile.save()

        messages.success(request, "Profile updated successfully ✅")
        return redirect("dashboard")

    return render(request, "profile/edit_profile.html", {
        "profile": profile
    })


# ---------- WELCOME / REGISTRATION ----------
@login_required(login_url="login")
def welcome(request):

    # Always get or create profile
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user
    )

    # If profile already completed, skip welcome
    if profile.is_profile_complete:
        return redirect("dashboard")

    if request.method == "POST":

        profile.track = request.POST.get("track")
        profile.education = request.POST.get("education")
        profile.branch = request.POST.get("branch")
        profile.year = request.POST.get("year")
        profile.college = request.POST.get("college")
        profile.university = request.POST.get("university", "")
        profile.career_goal = request.POST.get("goal")
        profile.about = request.POST.get("about")
        profile.location = request.POST.get("location")
        profile.phone = request.POST.get("phone")

        # ✅ THIS IS THE KEY CHANGE
        profile.is_profile_complete = True

        profile.save()

        messages.success(
            request,
            "Profile completed successfully 🎉"
        )

        return redirect("dashboard")

    return render(request, "welcome.html", {
        "profile": profile
    })


# ---------- COLLEGES ----------
@login_required(login_url="login")
def college_track_select(request):
    return render(request, "colleges/track_select.html")


@login_required(login_url="login")
def btech_categories(request):
    return render(request, "colleges/btech_categories.html")


def course_tracks(request):
    tracks = [
        {
            "id": "engineering",
            "title": "Engineering",
            "subtitle": "BTech & integrated programs",
            "enabled": True,
            "url": "btech_courses",
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


# ---------- JOBS ----------
def jobs(request):
    opportunities = Opportunity.objects.filter(is_active=True)
    return render(request, "jobs.html", {
        "jobs": opportunities
    })


# ---------- PROJECTS ----------
def projects(request):
    projects = Project.objects.filter(is_active=True)
    return render(request, "projects.html", {
        "projects": projects
    })


# ---------- PAPERS ----------
def paper_select(request):
    return render(request, "colleges/paper_select.html")


def btech_previous_year_papers(request):
    return render(request, "colleges/btech_previous_year_papers.html")


def hospitality_previous_year_papers(request):
    return render(request, "colleges/hospitality_previous_year_papers.html")


def support(request):
    return render(request, "support.html")

def is_profile_complete(user):
    return StudentProfile.objects.filter(user=user).exists()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@csrf_exempt
def openai_ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    try:
        body = json.loads(request.body)
        message = body.get("message", "").strip()
        mode = body.get("mode", "career")

        if not message:
            return JsonResponse({"error": "Empty message"}, status=400)

        # ---------------- USER CONTEXT ----------------
        user_context = "User not logged in."

        if request.user.is_authenticated:
            try:
                profile = StudentProfile.objects.get(user=request.user)
                user_context = f"""
User profile:
- Track: {profile.track}
- Branch: {profile.branch}
- Year: {profile.year}
- Career goal: {profile.career_goal}
- College: {profile.college}
"""
            except StudentProfile.DoesNotExist:
                user_context = "User logged in, profile incomplete."

        # ---------------- OPENAI CALL ----------------
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CareerInnTech AI. "
                        "Give clear, practical, step-by-step career guidance "
                        "for Indian students. Use bullet points."
                    ),
                },
                {
                    "role": "system",
                    "content": user_context,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            temperature=0.6,
        )

        reply = response.choices[0].message.content.strip()
        return JsonResponse({"reply": reply})

    except Exception as e:
        print("OPENAI ERROR:", e)
        return JsonResponse(
            {"error": "AI service failed. Try again later."},
            status=500
        )
def ai_chat_page(request):
    return render(request, "ai/ai_chat.html")
