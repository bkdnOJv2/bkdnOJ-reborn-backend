from django.contrib import admin
from helpers.models import MyModelAdmin
from .models import Contest, ContestProblem

class ContestAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Contest, ContestAdmin)
admin.site.register(ContestProblem, ContestAdmin)
