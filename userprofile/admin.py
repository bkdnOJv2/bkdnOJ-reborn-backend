from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from helpers.models import AllFieldModelAdmin
from helpers.models import MyModelAdmin
from organization.models import Organization
from .models import UserProfile

class UserProfileAdmin(AllFieldModelAdmin):
    list_display = ('owner', 'first_name', 'last_name', 'avatar')
    M2M_OTHER_MODEL = Organization
    M2M_WIDGET_FIELD = 'orgs'

admin.site.register(UserProfile, UserProfileAdmin)
