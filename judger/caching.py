from django.core.cache import cache

from problem.utils import key_user_completed_ids, key_user_attempted_ids
from compete.utils import key_contest_attempted_ids, key_contest_completed_ids

def finished_submission(sub):
    profile = sub.user
    keys = [key_user_attempted_ids(profile), key_user_completed_ids(profile)]
    if hasattr(sub, 'contest'):
        participation = sub.contest.participation
        keys += [key_contest_attempted_ids(participation)]
        keys += [key_contest_completed_ids(participation)]
    cache.delete_many(keys)
