import organization
from organization.models import *
org = Organization.objects.first().memberships

for x in org:
    print(x.user, x.get_role())