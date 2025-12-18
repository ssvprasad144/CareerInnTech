from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'track',
        'education',
        'branch',
        'year',
        'college',
        'career_goal',
        'location',
        'created_at',
    )

    list_filter = (
        'track',
        'year',
        'location',
        'created_at',
    )

    search_fields = (
        'user__username',
        'college',
        'branch',
        'career_goal',
    )

    readonly_fields = ('created_at',)

    ordering = ('-created_at',)

    # 🔹 PASTE IT HERE (INSIDE THE CLASS)
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_students'] = StudentProfile.objects.count()
        return super().changelist_view(request, extra_context=extra_context)

from .models import College

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "annual_fee", "exam_type")
    list_filter = ("exam_type", "location")
    search_fields = ("name",)

from django.contrib import admin
from .models import UserProfile

admin.site.register(UserProfile)


from .models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "opportunity_type",
        "status",
        "package",
        "is_active",
        "created_at",
    )

    list_filter = (
        "opportunity_type",
        "status",
        "is_active",
    )

    search_fields = (
        "title",
        "companies",
    )

    list_editable = (
        "status",
        "is_active",
    )

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "difficulty",
        "tech_stack",
        "is_active",
        "created_at",
    )

    list_filter = (
        "difficulty",
        "is_active",
    )

    search_fields = (
        "title",
        "tech_stack",
    )

    list_editable = (
        "difficulty",
        "is_active",
    )

