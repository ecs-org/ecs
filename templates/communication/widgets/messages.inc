{% load humanize core communication %}

<h3>{% block title %}Nachrichten{% endblock %} ({{ page.paginator.count }})</h3>

<div class="messages_header">
<img src="{{ MEDIA_URL }}/images/core/sort.png" alt="sortieren" />
<a class="widget" href="{{ request.path }}?sort={% ifequal sort 'submission' %}-{% endifequal %}submission">Studie</a>
| <a class="widget" href="{{ request.path }}?sort={% ifequal sort 'user' %}-{% endifequal %}user">Person</a> 
| <a class="widget" href="{{ request.path }}?sort={% ifequal sort 'timestamp' %}-{% endifequal %}timestamp">Ältere/Neuere</a>

</div>
<ol class="messages">
{% for thread in page.object_list %}
    <li class="message {% cycle 'even' 'odd' %}">
        <span class="head">
            {% if thread.submission %}{{ thread.submission|ec_number }} - {% endif %}
            {% if incoming and thread.last_message.unread %} [NEU] {% endif %}
            {{ thread.last_message.timestamp|naturalday:'d.m.Y' }}, {{ thread.last_message.timestamp|date:'H:i'}}
        </span>
        <span class="{% if thread.last_message.unread %}unread{% endif %}"></span>
        <a class="title open-in-popup" href="{% url ecs.communication.views.read_thread thread_pk=thread.pk %}">{{ thread.subject|truncatewords:10 }}</a>
        <span class="user">{% block message_user %}{% endblock %}</span>
        <span class="actions">
            {% if not incoming %}
                <a class="open-in-widget" href="{% url ecs.communication.views.bump_message message_pk=thread.last_message.pk %}" title="Bump"><img src="{{ MEDIA_URL }}/images/core/arrow-circle.png" alt="bump" /></a>
            {% else %}
                <a class="open-in-popup" href="{% url ecs.communication.views.send_message reply_to_pk=thread.last_message.pk %}" title="Antworten"><img src="{{ MEDIA_URL }}/images/core/mail-reply.png" alt="antworten" /></a>
                <a class="open-in-popup" href="{% url ecs.communication.views.delegate_thread thread_pk=thread.pk %}" title="Delegieren"><img src="{{ MEDIA_URL }}/images/core/mail-forward.png" alt="delegieren" /></a>
            {% endif %}
            <a class="open-in-widget" href="{% url ecs.communication.views.close_thread thread_pk=thread.pk %}?next={{ request.path|urlencode }}" title="Erledigt"><img src="{{ MEDIA_URL }}/images/core/tick.png" alt="erledigt" /></a>
        </span>
    </li>
{% endfor %}
</ol>

<div class="paginator">
    {% block more_link %}{% endblock %}

    {% if page.has_previous %}
        <a class="open-in-widget" href="{{ request.path }}?p=1"><img src="{{ MEDIA_URL }}/images/core/control-skip-180.png" alt="Anfang" title="Anfang" /></a>
        <a class="open-in-widget" href="{{ request.path }}?p={{ page.previous_page_number }}&amp;sort={{ sort }}"><img src="{{ MEDIA_URL }}/images/core/control-double-180.png" alt="zurück" title="zurück" /></a>
    {% endif %}

    {{ page.number }} von {{ page.paginator.num_pages }}
    
    {% if page.has_next %}
        <a class="open-in-widget" href="{{ request.path }}?p={{ page.next_page_number }}&amp;sort={{ sort }}"><img src="{{ MEDIA_URL }}/images/core/control-double.png" alt="weiter" title="weiter" /></a>
        <a class="open-in-widget" href="{{ request.path }}?p={{ page.paginator.num_pages }}&amp;sort={{ sort }}"><img src="{{ MEDIA_URL }}/images/core/control-skip.png" alt="Ende" title="Ende" /></a>
    {% endif %}
    
</div>


