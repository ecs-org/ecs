# -*- coding: utf-8 -*-

from django.conf import settings

def ecs_settings(request):
    return {
        'use_textboxlist': getattr(settings, 'USE_TEXTBOXLIST', False),
    }


