from django.contrib.auth.models import User
from ecs.users.utils import get_full_name

def startup():
    # patch the user __unicode__ method, so the hash in the username field does not show up
    User.__unicode__ = get_full_name
