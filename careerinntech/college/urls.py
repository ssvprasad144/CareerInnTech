from django.urls import path
from .views import ts_eamcet_colleges, ap_eamcet_colleges

urlpatterns = [
    path("ts-eamcet/", ts_eamcet_colleges, name="ts_eamcet"),
    path("ap-eamcet/", ap_eamcet_colleges, name="ap_eamcet"),
    path("ai/chat/", views.ai_chat, name="ai_chat"),

]
