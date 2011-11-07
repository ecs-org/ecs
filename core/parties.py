from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group

from ecs.users.utils import sudo
from ecs.communication.utils import send_system_message_template


class Party(object):
    def __init__(self, organization=None, name=None, user=None, email=None, involvement=None, anonymous=False):
        self.organization = organization
        self._name = name
        self._email = email
        self.user = user
        self.involvement = involvement
        self._anonymous = anonymous
        
    @property
    def email(self):
        if self._email:
            return self._email
        if self.user:
            return self.user.email
        return None
    
    @property
    def name(self):
        name = self._name or self.user or self._email
        if self._anonymous or not name:
            return u'- anonymous -'
        return unicode(name)

class PartyList(list):
    def get_users(self):
        return set(p.user for p in self if p.user)
        
    def __contains__(self, u):
        return any(p.user == u for p in self)

    def send_message(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', [])
        users = self.get_users().difference(exclude)
        cc_group = kwargs.pop('cc_group', None)
        if cc_group:
            group = Group.objects.get(name=cc_group)
            users |= set(User.objects.filter(groups=group))
        for u in users:
            send_system_message_template(u, *args, **kwargs)

@sudo()
def get_presenting_parties(sf):
    parties = PartyList()
    parties += [Party(organization=sf.sponsor_name, name=sf.sponsor_contact.full_name, user=sf.sponsor, email=sf.sponsor_email, involvement=_("Sponsor"))]

    if sf.invoice:
        parties.append(Party(organization=sf.invoice_name, 
            name=sf.invoice_contact.full_name, 
            email=sf.invoice_email, 
            user=sf.invoice,
            involvement=_("Invoice")
        ))
    parties.append(Party(organization=sf.submitter_organisation, 
        name=sf.submitter_contact.full_name, 
        email=sf.submitter_email,
        user=sf.submitter,
        involvement=_("Submitter"),
    ))
    parties.append(Party(user=sf.presenter, involvement=_("Presenter")))
    parties.append(Party(user=sf.susar_presenter, involvement=_("Susar Presenter")))

    for i in sf.investigators.filter(main=True):
        parties.append(Party(organization=i.organisation, name=i.contact.full_name, user=i.user, email=i.email, involvement=_("Primary Investigator")))

    return parties

@sudo()
def get_reviewing_parties(sf):
    from ecs.users.middleware import current_user_store

    parties = PartyList()

    anonymous = current_user_store._previous_user and not current_user_store._previous_user.get_profile().is_internal
    from ecs.tasks.models import Task
    external_reviewer_pks = sf.submission.external_reviewers.all().values_list('pk', flat=True)
    for task in Task.objects.for_submission(sf.submission).filter(assigned_to__isnull=False, deleted_at__isnull=True).order_by('created_at').select_related('task_type').distinct():
        if task.assigned_to.pk in external_reviewer_pks:
            parties.append(Party(user=task.assigned_to, involvement=task.task_type.trans_name, anonymous=anonymous))
        else:
            parties.append(Party(user=task.assigned_to, involvement=task.task_type.trans_name))
    return parties

@sudo()
def get_meeting_parties(sf):
    from ecs.meetings.models import AssignedMedicalCategory
    from ecs.users.middleware import current_user_store

    parties = PartyList()
    anonymous = current_user_store._previous_user and not current_user_store._previous_user.get_profile().is_internal
    
    timetable_entries_q = sf.submission.timetable_entries.all().values('pk').query
    meetings_q = sf.submission.meetings.filter(timetable_entries__in=timetable_entries_q).values('pk').query
    meetings_q = sf.submission.meetings.all()
    assigned_medical_categories_q = AssignedMedicalCategory.objects.filter(
        meeting__in=sf.submission.meetings.all(),
        category__in=sf.submission.medical_categories.all(),
    ).values('pk').query

    # assigned to the top
    for user in User.objects.filter(meeting_participations__entry__in=timetable_entries_q).exclude(assigned_medical_categories__in=assigned_medical_categories_q):
        parties.append(Party(user=user, involvement=_("Meeting Participant"), anonymous=anonymous))

    # assigned for medical category
    for user in User.objects.filter(assigned_medical_categories__in=assigned_medical_categories_q):
        parties.append(Party(user=user, involvement=_("Meeting Participant (assigned for category)"), anonymous=anonymous))

    return parties

@sudo()
def get_involved_parties(sf):
    parties = PartyList()
    for f in (get_presenting_parties, get_reviewing_parties, get_meeting_parties):
        parties += f(sf)
    return parties
