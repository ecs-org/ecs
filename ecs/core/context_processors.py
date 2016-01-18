from django.conf import settings

def ecs_settings(request):
    return {
        'debug': settings.DEBUG,
    }
