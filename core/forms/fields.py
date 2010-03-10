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

class NullBooleanWidget(forms.widgets.NullBooleanSelect):
    def __init__(self, attrs=None):
        choices = ((u'1', u'-'), (u'2', u'Ja'), (u'3', u'Nein'))
        forms.widgets.Select.__init__(self, attrs, choices)

class NullBooleanField(forms.NullBooleanField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', NullBooleanWidget)
        super(NullBooleanField, self).__init__(*args, **kwargs)