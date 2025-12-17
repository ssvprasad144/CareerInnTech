from django.shortcuts import render

# import hardcoded data
from .data.ts_eamcet import HARDCODED_TS_EAMCET_COLLEGES
from .data.ap_eamcet import HARDCODED_AP_EAMCET_COLLEGES


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
