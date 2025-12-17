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
