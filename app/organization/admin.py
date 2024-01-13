# pylint: skip-file
from django.contrib import admin
from helpers.models import AllFieldModelAdmin
from .models import Organization
from userprofile.models import UserProfile

class OrganizationAdmin(AllFieldModelAdmin):
    M2M_WIDGET_FIELD = 'members'
    M2M_OTHER_MODEL = UserProfile

admin.site.register(Organization, OrganizationAdmin)
