from django.contrib import admin
from helpers.models import MyModelAdmin
from .models import Organization, OrgMembership
from userprofile.models import UserProfile

class OrganizationAdmin(MyModelAdmin):
    M2M_WIDGET_FIELD = 'members'
    M2M_OTHER_MODEL = UserProfile
    
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrgMembership, OrganizationAdmin)