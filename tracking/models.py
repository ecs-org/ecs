import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve

class ViewManager(models.Manager):
    def get_or_create_for_url(self, url):
        func, args, kwargs = resolve(url)
        try:
            path = "%s.%s" % (func.__module__, func.__name__)
        except AttributeError:
            path = "<unknown>"
        return self.get_or_create(path=path)

class View(models.Model):
    path = models.CharField(max_length=200, db_index=True, unique=True)
    objects = ViewManager()
    
    def __unicode__(self):
        return self.path

class Request(models.Model):
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    ip = models.IPAddressField(db_index=True)
    user = models.ForeignKey(User)
    url = models.TextField()
    view = models.ForeignKey(View)
    anchor = models.CharField(max_length=100, db_index=True, blank=True)
    title = models.TextField(blank=True)
    content_type = models.CharField(max_length=100)
    method = models.CharField(max_length=4, choices=[('GET', 'GET'), ('POST', 'POST')], db_index=True)
    
    def save(self, **kwargs):
        if not self.view_id:
            self.view, created = View.objects.get_or_create_for_url(self.url)
        super(Request, self).save(**kwargs)
    
    def __unicode__(self):
        return "%s %s <-> %s" % (self.method, self.url, self.view.path)