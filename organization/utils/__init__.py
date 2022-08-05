from django.core.cache import cache
from django.db.models import Case, Count, ExpressionWrapper, F, Max, When
from django.db.models.fields import FloatField
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_noop

from userprofile.models import UserProfile
from problem.models import Problem
from submission.models import Submission

CACHE_DURATION = 86400

def organizations_of_member(profile: UserProfile):
  key = 'org_member:%d' % profile.id
  result = cache.get(key)
  if result is None:
    from organization.serializers import OrganizationBasicSerializer
    orgs_id_set = set()
    member_of = []

    for org in profile.organizations.order_by('-depth').all():
        if org.id in orgs_id_set: continue
        orgs_id_set.add(org.id)

        data = OrganizationBasicSerializer(org).data
        data['sub_orgs'] = []

        trv = org
        while True:
            if trv.is_root(): break
            trv = trv.get_parent()

            if trv.id in orgs_id_set: break
            orgs_id_set.add(trv.id)

            parent_data = OrganizationBasicSerializer(trv).data
            parent_data['sub_orgs'] = [data]
            data = parent_data
        member_of.append(data)

    ## End for
    result = member_of

    # TODO: Reduce information down to ids only, storing extra information like this may lead to out of memory
    cache.set(key, result, CACHE_DURATION)
  return result

def clear_cache(profile: UserProfile):
  key = 'org_member:%d' % profile.id
  cache.delete(key)

def clear_cache_many(profile_list):
  keys = []
  for item in profile_list:
    keys.append('org_member:%d' % item.id)
  cache.delete_many(keys)
