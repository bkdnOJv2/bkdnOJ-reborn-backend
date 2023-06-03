from django.contrib import admin
from judger.models import Judge, Language

class JudgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'online', 'is_blocked', 'start_time', 'load', 'ping')

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'name', 'extension')


admin.site.register(Judge, JudgeAdmin)
admin.site.register(Language, LanguageAdmin)
