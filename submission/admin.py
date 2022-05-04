from django.contrib import admin
from submission.models import Submission, SubmissionSource

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'problem', 'language', 'time', 'memory', 'status', 'result')

class SubmissionSourceAdmin(admin.ModelAdmin):
    list_display = ('submission',)

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionSource, SubmissionSourceAdmin)