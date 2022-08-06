from django.core.cache import cache


def finished_submission(sub):
    keys = ['user_completed:%d' % sub.user_id, 'user_attempted:%s' % sub.user_id]
    if hasattr(sub, 'contest'):
        participation = sub.contest.participation
        keys += ['contest_completed:%d' % participation.id]
        keys += ['contest_attempted:%d' % participation.id]
    cache.delete_many(keys)
