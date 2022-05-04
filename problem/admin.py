from django.contrib import admin
from problem.models import Problem

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('shortname', 'title', 'is_published', 'points', 'submission_visibility_mode')

admin.site.register(Problem, ProblemAdmin)
