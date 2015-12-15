from django.db import models


class Foo(models.Model):
    flag = models.BooleanField(default=False)


class FooReview(models.Model):
    name = models.CharField(max_length=30)
