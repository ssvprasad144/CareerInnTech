from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html', {
        'show_dashboard_header': False
    })

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
        user.save()

        login(request, user)          # 👈 auto login user
        return redirect('welcome')    # 👈 redirect to new page

    return render(request, 'signup.html')





def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')



def logout_view(request):
    logout(request)
    return redirect('home')

def about(request):
    return render(request, 'about.html', {
        'show_dashboard_header': False
    })

def contact(request):
    return render(request, 'contact.html', {
        'show_dashboard_header': False
    })

@login_required(login_url='login')
def dashboard(request):
    # 🚨 If profile not created yet, force welcome page
    if not StudentProfile.objects.filter(user=request.user).exists():
        return redirect('welcome')

    return render(request, 'dashboard.html')




from .models import StudentProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

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
