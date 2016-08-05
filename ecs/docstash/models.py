import uuid

from django.db import models
from django.http import QueryDict
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django_extensions.db.fields.json import JSONField


class DocStash(models.Model):
    class ConcurrentModification(Exception):
        pass

    key = models.UUIDField(default=uuid.uuid4, primary_key=True)
    group = models.CharField(max_length=120, db_index=True, null=True)
    current_version = models.IntegerField(default=-1)
    owner = models.ForeignKey(User)
    modtime = models.DateTimeField(auto_now=True)
    name = models.TextField(blank=True, null=True)
    value = JSONField(null=False)
    
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    parent_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('group', 'owner', 'content_type', 'object_id')

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __delitem__(self, key):
        del self.value[key]

    def __contains__(self, key):
        return key in self.value

    def get(self, name, default=None):
        return self.value.get(name, default)

    @property
    def POST(self):
        if 'POST' in self.value:
            return QueryDict(self.value['POST'])
        return None

    @POST.setter
    def POST(self, data):
        self.value['POST'] = data.urlencode()

    def save(self, **kwargs):
        if DocStash.objects.filter(key=self.key).exists():
            updated = DocStash.objects.filter(
                key=self.key, current_version=self.current_version
            ).update(current_version=models.F('current_version') + 1)
            if not updated:
                raise self.ConcurrentModification()

        self.current_version += 1
        return super().save(**kwargs)
