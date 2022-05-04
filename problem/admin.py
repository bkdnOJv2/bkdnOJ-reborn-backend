from django.contrib import admin
from problem.models import Problem, ProblemTestProfile, TestCase

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('shortname', 'title', 'is_published', 'points', 'submission_visibility_mode')

class ProblemTestProfileAdmin(admin.ModelAdmin):
    pass

class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('test_profile', 'order', 'is_pretest', 'points', 'input_file', 'output_file')

admin.site.register(Problem, ProblemAdmin)
admin.site.register(ProblemTestProfile, ProblemTestProfileAdmin)
admin.site.register(TestCase, TestCaseAdmin)
