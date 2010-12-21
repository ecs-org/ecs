# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from ecs.users.utils import hash_email

class EmailAuthBackend(ModelBackend):
    def authenticate(self, email=None, password=None):
        username = hash_email(email)
        return super(EmailAuthBackend, self).authenticate(username=username, password=password)

