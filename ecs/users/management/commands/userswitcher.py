from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User, Group
from ecs.users.utils import get_user

class Command(BaseCommand):
    help = "add or remove users from the userswitcher"
    option_list = BaseCommand.option_list + (
        make_option('-i', action='store_true', dest='activate_internal', help='add is_internal users to the userswitcher'),
        make_option('-I', action='store_false', dest='activate_internal', help='remove is_internal users from the userswitcher'),
        make_option('-t', action='store_true', dest='activate_testusers', help='add testusers to the userswitcher'),
        make_option('-T', action='store_false', dest='activate_testusers', help='remove testusers from the userswitcher'),
        make_option('-m', action='store_true', dest='activate_board', help='add board member users to the userswitcher'),
        make_option('-M', action='store_false', dest='activate_board', help='remove board member users from the userswitcher'),
        make_option('-r', action='store_true', dest='remove_user', help='remove users from the userswitcher'),
    )
    def handle(self, *emails, **options):
        verbosity = int(options['verbosity'])
        activate_internal = options['activate_internal']
        activate_testusers = options['activate_testusers']
        activate_boardmember = options['activate_board']
        remove_user = options['remove_user']

        if activate_internal is None and activate_testusers is None and activate_boardmember is None and not emails:
            raise CommandError("nothing to do")

        if remove_user and not emails:
            raise CommandError("nobody to remove")

        group = Group.objects.get(name='Userswitcher Target')
        boardmember_group = Group.objects.get(name="EC-Board Member")
        internal_users = User.objects.filter(profile__is_internal=True).exclude(profile__is_testuser=True)
        testusers = User.objects.filter(profile__is_testuser=True)
        boardmembers = User.objects.filter(groups=boardmember_group.id)

        def _toggle(user, activate):
            if verbosity >= 2:
                print('  {0}{1}'.format('+' if activate else '-', user.email))
            (group.user_set.add if activate else group.user_set.remove)(user)

        def _toggle_set(name, users, activate):
            if not activate is None:
                if verbosity >= 1:
                    print(('+' if activate else '-') + name)
                for user in users:
                    _toggle(user, activate)

        _toggle_set('internal_users', internal_users, activate_internal)
        _toggle_set('testusers', testusers, activate_testusers)
        _toggle_set('boardmembers', boardmembers, activate_boardmember)

        for email in emails:
            user = get_user(email)
            _toggle(user, not remove_user)
