from django.core.cache import cache
from django.db.models import Case, Count, ExpressionWrapper, F, Max, When
from django.db.models.fields import FloatField
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_noop

from userprofile.models import UserProfile
from problem.models import Problem
from submission.models import Submission

CACHE_DURATION = 86400

from organization.serializers import OrganizationBasicSerializer
def __build_tree(org, ids_set):
  dat = OrganizationBasicSerializer(org).data
  dat['sub_orgs'] = []
  for child_org in org.get_children():
    if child_org.id in ids_set:
      dat['sub_orgs'].append( __build_tree(child_org, ids_set) )

  return dat

def organizations_of_member(profile: UserProfile):
  key = 'org_member:%d' % profile.id
  result = cache.get(key)
  if result is None:
    member_org_ids = set( profile.organizations.values_list('id', flat=True) )

    orgs_id_set = set()
    member_of = []

    for org in profile.organizations.filter(depth=1).all():
      if org.id in member_org_ids:
        member_of.append( __build_tree(org, member_org_ids) )

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
