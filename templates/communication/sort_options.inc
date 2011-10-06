{% load i18n %}
<span class="icon_sort">{% trans "sort" %}</span>
{% if not submission %}
<a{% if widget %} class="open-in-widget"{% endif %} href="{{ request.path }}?sort={% ifequal sort 'submission' %}-{% endifequal %}submission">Studie</a> |
{% endif %}
<a{% if widget %} class="open-in-widget"{% endif %} href="{{ request.path }}?sort={% if sort == 'user' %}-{% endif %}user">{% trans "Person" %}</a> 
| <a{% if widget %} class="open-in-widget"{% endif %} href="{{ request.path }}?sort={% if sort == 'last_message__timestamp' %}-{% endif %}last_message__timestamp">{% trans "Old/New" %}</a>

