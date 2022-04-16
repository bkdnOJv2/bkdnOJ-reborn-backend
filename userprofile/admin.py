from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('owner', 'first_name', 'last_name', 'avatar')

admin.site.register(UserProfile, UserProfileAdmin)