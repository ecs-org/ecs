import uuid

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from picklefield.fields import PickledObjectField


class DocStash(models.Model):
    class ConcurrentModification(Exception):
        pass

    key = models.UUIDField(default=uuid.uuid4, primary_key=True)
    group = models.CharField(max_length=120, db_index=True, null=True)
    current_version = models.IntegerField(default=-1)
    owner = models.ForeignKey(User)
    modtime = models.DateTimeField(auto_now=True)
    name = models.TextField(blank=True, null=True)
    value = PickledObjectField(compress=True, default=dict)
    
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    parent_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('group', 'owner', 'content_type', 'object_id')

    def __getitem__(self, name):
        return self.value[name]

    def __setitem__(self, name, value):
        val = self.value
        val[name] = value
        self.value = val

    def get(self, name, default=None):
        return self.value.get(name, default)

    def update(self, d):
        val = self.value
        val.update(d)
        self.value = val

    def save(self, **kwargs):
        if DocStash.objects.filter(key=self.key).exists():
            updated = DocStash.objects.filter(
                key=self.key, current_version=self.current_version
            ).update(current_version=models.F('current_version') + 1)
            if not updated:
                raise self.ConcurrentModification()

        self.current_version += 1
        return super(DocStash, self).save(**kwargs)
