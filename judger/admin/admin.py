from django.contrib import admin
from judger.models import Judge, RuntimeVersion

class JudgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'online', 'is_blocked', 'start_time', 'load', 'ping')

admin.site.register(Judge, JudgeAdmin)
