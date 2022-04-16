from django.db import models
from django_extensions.db.models import TimeStampedModel

class Organization(TimeStampedModel):
	shortname = models.SlugField(db_index=True, unique=True)
	name = models.CharField(max_length=256, null=False, blank=False)
	description = models.TextField(null=False, blank=False)