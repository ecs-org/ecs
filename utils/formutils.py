# -*- coding: utf-8 -*-

from django.core.validators import EMPTY_VALUES

def require_fields(form, fields):
    for f in fields:
        if f not in form.cleaned_data or form.cleaned_data[f] in EMPTY_VALUES:
            form._errors[f] = form.error_class([form.fields[f].error_messages['required']])


