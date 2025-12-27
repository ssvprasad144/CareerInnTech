from django.shortcuts import render

# import hardcoded data
from .data.ts_eamcet import HARDCODED_TS_EAMCET_COLLEGES
from .data.ap_eamcet import HARDCODED_AP_EAMCET_COLLEGES
import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt







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
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse(
            {"reply": "Please login to use AI Career Bot."},
            status=401
        )

    user_message = request.POST.get("message", "").strip()
    if not user_message:
        return JsonResponse({"reply": "Please ask a valid question."})

    # Safe profile access
    profile = getattr(request.user, "profile", None)

    if profile:
        student_context = f"""
Name: {profile.name}
College: {profile.college}
Branch: {profile.branch}
Year: {profile.year}
Interests: {profile.interests}
"""
    else:
        student_context = f"""
Name: {request.user.username}
College: Not provided
Branch: Not provided
Year: Not provided
Interests: Not provided
"""

    system_prompt = f"""
You are an AI Career Assistant.

Student details:
{student_context}

Rules:
- Answer ONLY student-related questions
- Be simple and practical
- ALWAYS end with:
"👉 Please connect with mentors for personalized guidance."
"""

    payload = {
        "model": "grok-2",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROK_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return JsonResponse({
                "reply": f"Grok error {response.status_code}: {response.text}"
            })

        data = response.json()
        reply = data["choices"][0]["message"]["content"]

        return JsonResponse({"reply": reply})

    except Exception as e:
        return JsonResponse({
            "reply": f"AI error: {str(e)}"
        })

import json
from openai import OpenAI
client = OpenAI()

@csrf_exempt
def translate_bulk(request):
    if request.method != "POST":
        return JsonResponse({"translations": []})

    try:
        data = json.loads(request.body)
        texts = data.get("texts", [])
        lang = data.get("lang")

        if not texts or not lang:
            return JsonResponse({"translations": []})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Translate the following texts into {lang}. Keep meaning. Return each translation on a new line."
                },
                {
                    "role": "user",
                    "content": "\n".join(texts)
                }
            ]
        )

        translated = response.choices[0].message.content.split("\n")

        return JsonResponse({
            "translations": translated
        })

    except Exception as e:
        return JsonResponse({
            "translations": [],
            "error": str(e)
        })

