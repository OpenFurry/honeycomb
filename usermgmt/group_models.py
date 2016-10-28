from django.contrib.auth.models import User
from django.db import models


class FriendGroup(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
