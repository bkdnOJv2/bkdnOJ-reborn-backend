from django.db import models

class Organization(models.Model):
	shortname = models.SlugField(
		db_index=True,
		unique=True,
	)
	name = models.CharField(max_length=256, null=False, blank=False)
	description = models.TextField(null=False, blank=False)