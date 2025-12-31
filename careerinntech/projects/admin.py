from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "track",
        "project_type",
        "is_active",
        "is_premium",
    )

    list_filter = ("track", "project_type", "is_active", "is_premium")
    search_fields = ("title", "description")
