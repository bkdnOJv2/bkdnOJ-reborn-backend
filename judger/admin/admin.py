from django.contrib import admin
from judger.models import Judge, Language, LanguageLimit

class JudgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'online', 'is_blocked', 'start_time', 'load', 'ping')

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'name', 'extension')

class LanguageLimitAdmin(admin.ModelAdmin):
    list_display = ('language', 'problem', 'time_limit', 'memory_limit')

admin.site.register(Judge, JudgeAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(LanguageLimit, LanguageLimitAdmin)
