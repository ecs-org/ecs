from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.utils import timezone

from ecs.users.utils import sudo, get_current_user
from ecs.communication.utils import send_system_message_template
from ecs.tasks.models import Task


class Party(object):
    def __init__(self, organization=None, name=None, user=None, email=None, involvement=None, anonymous=False):
        self.organization = organization
        self._name = name
        self._email = email
        self._user = user
        self.involvement = involvement
        self.anonymous = anonymous

    @property
    def email(self):
        if not self.anonymous:
            if self._email:
                return self._email
            if self.user:
                return self.user.email
        return None

    @property
    def name(self):
        name = self._name or self.user or self._email
        if self.anonymous or not name:
            return '- anonymous -'
        return str(name)

    @property
    def user(self):
        if not self.anonymous:
            return self._user
        return None

    def __eq__(self, other):
        if not isinstance(other, Party):
            return False
        return all(getattr(self, attr) == getattr(other, attr) for attr in ('organization', '_name', '_email', '_user', 'involvement', 'anonymous'))

    def __repr__(self):
        return str(self.email)


class PartyList(list):
    def get_users(self):
        return set(p.user for p in self if p.user)
        
    def __contains__(self, u):
        if isinstance(u, Party):
            return super().__contains__(u)
        return any(p.user == u for p in self)

    def send_message(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', [])
        users = self.get_users().difference(exclude)
        for u in users:
            send_system_message_template(u, *args, **kwargs)

    def add(self, *args, **kwargs):
        self.append(Party(*args, **kwargs))

def get_presenting_parties(sf):
    parties = PartyList()
    parties.add(organization=sf.submitter_organisation, name=sf.submitter_contact.full_name,
        email=sf.submitter_email, user=sf.submitter, involvement=_("Submitter"))
    parties.add(organization=sf.sponsor_name, name=sf.sponsor_contact.full_name,
        email=sf.sponsor_email, user=sf.sponsor, involvement=_("Sponsor"))
    parties.add(user=sf.submission.presenter, involvement=_("Presenter"))
    parties.add(user=sf.submission.susar_presenter, involvement=_("Susar Presenter"))
    for i in sf.investigators.filter(main=True):
        parties.add(organization=i.organisation, name=i.contact.full_name, user=i.user, email=i.email, involvement=_("Primary Investigator"))
    return parties

def get_reviewing_parties(sf, active=None):
    parties = PartyList()

    anonymous = get_current_user() and not get_current_user().profile.is_internal
    with sudo():
        tasks = Task.objects.for_submission(sf.submission).filter(assigned_to__isnull=False, deleted_at__isnull=True).exclude(task_type__workflow_node__uid='resubmission').order_by('created_at').select_related('task_type').distinct()
        if active:
            tasks = tasks.open()
        tasks = list(tasks)
    for task in tasks:
        if task.task_type.workflow_node.uid == 'external_review':
            parties.add(user=task.assigned_to, involvement=task.task_type.trans_name, anonymous=anonymous)
        else:
            party = Party(user=task.assigned_to, involvement=task.task_type.trans_name)
            if party not in parties:
                parties.append(party)
    for temp_auth in sf.submission.temp_auth.filter(end__gt=timezone.now()):
        parties.add(user=temp_auth.user, involvement=_('Temporary Authorization'))
    return parties

def get_involved_parties(sf):
    p = get_presenting_parties(sf)
    p += get_reviewing_parties(sf)
    return p
