# pylint: skip-file
from django.contrib import admin
from helpers.models import AllFieldModelAdmin
from .models import *

class ContestAdmin(AllFieldModelAdmin):
    pass

admin.site.register(Contest, ContestAdmin)
admin.site.register(ContestProblem, ContestAdmin)
admin.site.register(ContestParticipation, ContestAdmin)
admin.site.register(ContestSubmission, ContestAdmin)
admin.site.register(Rating, ContestAdmin)
