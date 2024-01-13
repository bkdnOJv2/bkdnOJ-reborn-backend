# pylint: skip-file
from django.db import models
from django.db.models import CASCADE 
from django.utils.translation import gettext, gettext_lazy as _


from userprofile.models import UserProfile as Profile

__all__ = ['Rating']

class Rating(models.Model):
    user = models.ForeignKey(Profile, verbose_name=_('user'), related_name='ratings', on_delete=CASCADE)
    contest = models.ForeignKey("compete.Contest", verbose_name=_('contest'), related_name='ratings', on_delete=CASCADE)
    participation = models.OneToOneField("compete.ContestParticipation", verbose_name=_('participation'),
                                         related_name='rating', on_delete=CASCADE)
    rank = models.IntegerField(verbose_name=_('rank'))
    rating = models.IntegerField(verbose_name=_('rating'))
    mean = models.FloatField(verbose_name=_('raw rating'))
    performance = models.FloatField(verbose_name=_('contest performance'))
    last_rated = models.DateTimeField(db_index=True, verbose_name=_('last rated'))

    class Meta:
        unique_together = ('user', 'contest')
        verbose_name = _('contest rating')
        verbose_name_plural = _('contest ratings')