# pylint: skip-file
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe    

from problem.models import Problem, ProblemTestProfile, TestCase, LanguageLimit

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('shortname', 'title', 'is_public', 'points', 'submission_visibility_mode', 'test_profile_link')

    readonly_fields = ('test_profile_link',)

    def test_profile_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:problem_problemtestprofile_change', args=(obj.test_profile.problem,)),
            'To Profile'
        ))
    test_profile_link.short_description = 'Test Data Profile'

admin.site.register(Problem, ProblemAdmin)

class ProblemTestProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'modified')

admin.site.register(ProblemTestProfile, ProblemTestProfileAdmin)

from django.contrib.admin import SimpleListFilter

class ProblemFilter(SimpleListFilter):
    title = 'problem' 
    parameter_name = 'problem'

    def lookups(self, request, model_admin):
        problem_profiles = set([t.test_profile for t in model_admin.model.objects.all()])
        return [(p.problem, p.problem) for p in problem_profiles]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(test_profile__problem__exact=self.value())
    

class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('test_profile', 'order', 'is_pretest', 'points', 'input_file', 'output_file')
    list_filter = (ProblemFilter,)

admin.site.register(TestCase, TestCaseAdmin)

class LanguageLimitAdmin(admin.ModelAdmin):
    list_display = ('language', 'problem', 'time_limit', 'memory_limit')
admin.site.register(LanguageLimit, LanguageLimitAdmin)

