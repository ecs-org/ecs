from django import forms

from ecs.core.models import Investigator

DATE_INPUT_FORMATS = ("%d.%m.%Y", "%Y-%m-%d")

class DateField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('input_formats', DATE_INPUT_FORMATS)
        super(DateField, self).__init__(*args, **kwargs)

class InvestigatorChoiceMixin(object):
    def __init__(self, **kwargs):
        kwargs.setdefault('queryset', Investigator.objects.order_by('name'))
        super(InvestigatorChoiceMixin, self).__init__(**kwargs)

    def label_from_instance(self, obj):
        return u"%s (%s)" % (obj.name, obj.ethics_commission.name)

class InvestigatorChoiceField(InvestigatorChoiceMixin, forms.ModelChoiceField): pass
class InvestigatorMultipleChoiceField(InvestigatorChoiceMixin, forms.ModelMultipleChoiceField): pass
