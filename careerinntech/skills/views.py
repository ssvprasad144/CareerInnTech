from django.shortcuts import render

def btech_skills(request):
    return render(request, "skills/btech_skills.html")

def btech_branch(request):
    return render(request, "skills/btech_branch.html")

def btech_view_all(request):
    return render(request, "skills/btech_view_all.html")

def course_detail(request):
    return render(request, "skills/course_detail.html")
