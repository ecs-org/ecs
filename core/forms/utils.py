from django import forms

def mark_readonly(form):
    for field in form.fields.itervalues():
        field.widget.attrs['readonly'] = 'readonly'
        field.widget.attrs['disabled'] = 'disabled'


class ReadonlyFormMixin(object):
    def __init__(self, *args, **kwargs):
        readonly = kwargs.pop('readonly', False)
        super(ReadonlyFormMixin, self).__init__(*args, **kwargs)
        if readonly:
            mark_readonly(self)


class ReadonlyFormSetMixin(object):
    def __init__(self, *args, **kwargs):
        readonly = kwargs.pop('readonly', False)
        extra = kwargs.pop('extra', None)
        if extra is not None:
            self.extra = extra
        super(ReadonlyFormSetMixin, self).__init__(*args, **kwargs)
        if readonly:
            for form in self.forms:
                mark_readonly(form)

