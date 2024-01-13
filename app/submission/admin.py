# pylint: skip-file
from django.urls import reverse
from django.utils.safestring import mark_safe    
from django.contrib import admin
from submission.models import Submission, SubmissionSource, SubmissionTestCase

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'problem', 'language', 'time', 'memory', 'status', 'result', 'source_link')
    readonly_fields = ('source_link',)

    def source_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:submission_submissionsource_change', args=(obj.source.id,)),
            'Source Code'
        ))
    source_link.short_description = 'Source code'

class SubmissionSourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SubmissionSource._meta.get_fields()]

class SubmissionTestCaseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SubmissionTestCase._meta.get_fields()]

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionSource, SubmissionSourceAdmin)
admin.site.register(SubmissionTestCase, SubmissionTestCaseAdmin)

