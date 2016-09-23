from django import template

from ecs.core.models import AdvancedSettings


register = template.Library()


@register.simple_tag(takes_context=True)
def load_vote_extra(context):
    s = AdvancedSettings.objects.get()
    context.update({
        'vote1_extra': s.vote1_extra,
        'vote2_extra': s.vote2_extra,
        'vote3a_extra': s.vote3a_extra,
        'vote3b_extra': s.vote3b_extra,
        'vote4_extra': s.vote4_extra,
        'vote5_extra': s.vote5_extra,
        'vote_pdf_extra': s.vote_pdf_extra,
    })
    return ''
