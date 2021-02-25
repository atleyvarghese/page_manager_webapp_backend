from django.contrib.auth.models import User

# class User(AbstractUser):
#     """
#     Users within the Django authentication system are represented by this
#     model.
#     Email and password are required.
#     """
#
#
#
#
#     class Meta(object):
#         unique_together = ('email', )


# from django.contrib.auth.models import AbstractUser
from django.db import models


class FacebookProfile(models.Model):
    """
    """
    facebook_account_id = models.BigIntegerField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='facebook_profile')
    primary_access_token = models.TextField()
    oauth_access_token = models.TextField(null=True, blank=True)
