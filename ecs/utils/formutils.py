from django.core.validators import EMPTY_VALUES
from django.db.models import QuerySet


def require_fields(form, fields):
    for f in fields:
        val = form.cleaned_data.get(f, None)
        if val in EMPTY_VALUES or \
            (isinstance(val, QuerySet) and not val.exists()):
            form.add_error(f, form.fields[f].error_messages['required'])
