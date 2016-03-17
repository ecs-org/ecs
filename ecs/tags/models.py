from django.db import models
from django.core.validators import RegexValidator


class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True,
        validators=[RegexValidator(r'^[A-Za-z0-9._-]{1,25}$')])
    color = models.IntegerField()

    # XXX: This could be any model instead, but let's not complicate matters as
    # long as we don't need to.
    submissions = models.ManyToManyField('core.Submission', related_name='tags')

    class Meta:
        ordering = ('name',)

    @property
    def bg_color(self):
        return '#{:06x}'.format(self.color)

    @property
    def text_color(self):
        r = self.color >> 16
        g = self.color >> 8 & 0xff
        b = self.color & 0xff
        brightness = (r * 299 + g * 587 + b * 114) // 1000
        return '#000000' if brightness >= 128 else '#ffffff'

    @property
    def css(self):
        return 'background-color: {}; color: {};'.format(
            self.bg_color, self.text_color)
