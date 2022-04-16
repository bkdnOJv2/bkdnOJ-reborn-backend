from django.conf import settings
from django.db import models

class UserProfile(models.Model):
	owner = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		primary_key=True,
	)
	first_name = models.CharField(max_length=150)
	last_name = models.CharField(max_length=150)
	avatar = models.ImageField(upload_to='avatar/', null=True)

	description = models.TextField()

	# orgs
	# 

	def __str__(self):
		return "{}'s profile".format(self.owner.username)
