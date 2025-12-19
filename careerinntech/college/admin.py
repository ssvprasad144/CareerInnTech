from django.contrib import admin
from .models import BranchVideo

@admin.register(BranchVideo)
class BranchVideoAdmin(admin.ModelAdmin):
    list_display = ("branch", "is_active", "updated_at")
    list_editable = ("is_active",)
