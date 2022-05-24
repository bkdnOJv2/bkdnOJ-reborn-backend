from django.urls import reverse
from django.utils.safestring import mark_safe    
from django.contrib import admin
from submission.models import Submission, SubmissionSource

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
    list_display = ('submission',)

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionSource, SubmissionSourceAdmin)
