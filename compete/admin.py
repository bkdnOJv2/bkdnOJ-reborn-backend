from django.contrib import admin
from helpers.models import MyModelAdmin
from .models import Contest, ContestProblem, \
    ContestParticipation, ContestSubmission

class ContestAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Contest, ContestAdmin)
admin.site.register(ContestProblem, ContestAdmin)
admin.site.register(ContestParticipation, ContestAdmin)
admin.site.register(ContestSubmission, ContestAdmin)

