from django.shortcuts import render

# import hardcoded data
from .data.ts_eamcet import HARDCODED_TS_EAMCET_COLLEGES
from .data.ap_eamcet import HARDCODED_AP_EAMCET_COLLEGES
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings


settings.GROK_API_KEY


@login_required
def ai_page(request):
    return render(request, "ai/ai_chat.html")



def apply_filters(colleges, request):
    location = request.GET.get("location", "").strip()
    fee = request.GET.get("fee", "").strip()
    rank = request.GET.get("rank", "").strip()

    filtered = colleges

    if location:
        filtered = [
            c for c in filtered
            if c.get("location", "").lower() == location.lower()
        ]

    if fee:
        try:
            fee = int(fee)
            if fee == 1:
                filtered = [c for c in filtered if c["annual_fee"] < 100000]
            elif fee == 2:
                filtered = [
                    c for c in filtered
                    if 100000 <= c["annual_fee"] <= 200000
                ]
            elif fee == 3:
                filtered = [c for c in filtered if c["annual_fee"] > 200000]
        except ValueError:
            pass

    if rank:
        try:
            rank = int(rank)
            filtered = [
                c for c in filtered
                if rank <= c.get("closing_rank", 0)
            ]
        except ValueError:
            pass

    return filtered


# ---------- TS EAMCET ----------
def ts_eamcet_colleges(request):
    colleges = apply_filters(HARDCODED_TS_EAMCET_COLLEGES, request)
    return render(request, "colleges/ts_eamcet_colleges.html", {
        "hardcoded_colleges": colleges,
        "admin_colleges": []
    })


# ---------- AP EAMCET ----------
def ap_eamcet_colleges(request):
    colleges = apply_filters(HARDCODED_AP_EAMCET_COLLEGES, request)
    return render(request, "colleges/ap_eamcet_colleges.html", {
        "hardcoded_colleges": colleges,
        "admin_colleges": []
    })

from .models import BranchVideo

def cse_branch(request):
    video = BranchVideo.objects.filter(
        branch="cse",
        is_active=True
    ).first()

    return render(request, "colleges/branches/cse.html", {
        "video": video
    })
@csrf_exempt
@login_required
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"reply": "Please login to use AI Career Bot."})

    user_message = request.POST.get("message", "").strip()
    if not user_message:
        return JsonResponse({"reply": "Please ask a valid question."})

    # Assuming you already have Profile linked to User
    profile = request.user.profile

    system_prompt = f"""
You are an AI assistant for students.

Student details:
Name: {profile.name}
College: {profile.college}
Branch: {profile.branch}
Year: {profile.year}
Interests: {profile.interests}

Rules:
- Answer ONLY student-related questions (career, exams, skills, internships)
- Be clear and simple
- Avoid complex jargon
- ALWAYS end with:
"👉 Please connect with mentors for personalized guidance."
"""

    payload = {
        "model": "grok-beta",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROK_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=20
        )

        ai_reply = response.json()["choices"][0]["message"]["content"]
        return JsonResponse({"reply": ai_reply})

    except Exception as e:
        return JsonResponse({
            "reply": "AI is currently busy. Please try again later."
        })

