from django.contrib import admin
from problem.models import Problem, ProblemTestProfile, TestCase, LanguageLimit

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('shortname', 'title', 'is_published', 'points', 'submission_visibility_mode')

admin.site.register(Problem, ProblemAdmin)

class ProblemTestProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(ProblemTestProfile, ProblemTestProfileAdmin)

class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('test_profile', 'order', 'is_pretest', 'points', 'input_file', 'output_file')
admin.site.register(TestCase, TestCaseAdmin)

class LanguageLimitAdmin(admin.ModelAdmin):
    list_display = ('language', 'problem', 'time_limit', 'memory_limit')
admin.site.register(LanguageLimit, LanguageLimitAdmin)

