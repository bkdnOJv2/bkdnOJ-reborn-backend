from django.contrib import admin
from helpers.models import MetaInferTimestampedModelAdmin
from .models import Organization, OrgMembership

class OrganizationAdmin(MetaInferTimestampedModelAdmin):
    pass
    
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrgMembership, OrganizationAdmin)