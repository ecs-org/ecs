import anyjson
from functools import wraps

from djcelery.models import CrontabSchedule, IntervalSchedule, PeriodicTask

from django.conf import settings
from django.utils import translation


def make_periodic_interval_task(name, task, every_sec, *args, **kwargs):
    '''creates a new periodic interval task, with name=name, updates fields if already exists'''
    pt, created = PeriodicTask.objects.get_or_create(name= name)

    if pt.crontab:
        print("Warning, old task entry had a crontab")
        if pt.crontab.periodictask_set.count() == 1:
            print("Was the only one used , deleting it")
            ct = pt.crontab
            ct.delete()
            pt.crontab = None
    
    if not pt.interval:
        i= IntervalSchedule()
    else:
        i= pt.interval
    
    i.period = "seconds"
    i.every = str(every_sec)
    i.save()
    
    pt.interval = i
    pt.task = task
    pt.args = anyjson.serialize(args)
    pt.kwargs = anyjson.serialize(kwargs)
    pt.save()
    print ("saved task: %s, created: %s" % (str(pt), str(created)))
        

def make_periodic_crontab_task(name, task, minute, hour, day_of_week, *args, **kwargs):
    '''creates a new periodic crontab task, with name=name, updates fields if already exists'''
    pt, created = PeriodicTask.objects.get_or_create(name= name)
    
    if pt.interval:
        print("Warning, old task entry had an interval")
        if pt.interval.periodictask_set.count() == 1:
            print("Was the only one, deleting it")
            i = pt.interval
            i.delete()
            pt.interval = None
    
    if not pt.crontab:
        ct= CrontabSchedule()
    else:
        ct= pt.crontab
    
    ct.minute = minute
    ct.hour = hour
    ct.day_of_week = day_of_week
    ct.save()
    
    pt.crontab = ct
    pt.task = task
    pt.args = anyjson.serialize(args)
    pt.kwargs = anyjson.serialize(kwargs)
    pt.save()
    print ("saved task: %s, created: %s" % (str(pt), str(created)))


def translate(func):
    @wraps(func)
    def _inner(*args, **kwargs):
        lang = kwargs.pop('language', settings.LANGUAGE_CODE)
        prev_lang = translation.get_language()
        translation.activate(lang)
        try:
            ret = func(*args, **kwargs)
        finally:
            translation.activate(prev_lang)
        return ret
    return _inner
