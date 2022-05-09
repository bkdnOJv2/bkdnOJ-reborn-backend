from distutils.command.upload import upload
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from helpers.fileupload import \
    path_and_rename_avatar, DEFAULT_AVATAR_URL
from organization.models import OrgMembership

class UserProfile(TimeStampedModel):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, primary_key=True,
        related_name='profile',
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    description = models.TextField()

    avatar = models.ImageField( upload_to=path_and_rename_avatar,
        default=DEFAULT_AVATAR_URL
    )

    global_ranking = models.BigIntegerField(default=0)

    orgs = models.ManyToManyField(
        'organization.Organization', through=OrgMembership
    )

    @property
    def member_of_orgs(self):
        member_of_orgs = OrgMembership.objects.filter(user=self)
        return member_of_orgs

    def set_image_to_default(self):
        self.avatar.delete(save=False) # delete old image file
        self.avatar = DEFAULT_AVATAR_URL
        self.save()
    
    class Meta:
        ordering = ['owner']
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

        default_permissions = ( 
            'view', 'change', #'add', 'delete'
        )
        permissions = (
            # (, _()),
        )

    def __str__(self):
        name = f"{self.first_name} {self.last_name}"
        if not name.strip():
            name = "no name given"
        return f"@{self.owner.username} ({name})"
