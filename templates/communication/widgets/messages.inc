{% load humanize i18n core communication %}

<h3>{% block title %}Nachrichten{% endblock %} ({{ page.paginator.count }})</h3>

<div class="messages_header">
<span class="icon_sort">{% trans "sort" %}</span>
<a class="open-in-widget" href="{{ request.path }}?sort={% ifequal sort 'submission' %}-{% endifequal %}submission">Studie</a>
| <a class="open-in-widget" href="{{ request.path }}?sort={% ifequal sort 'user' %}-{% endifequal %}user">Person</a> 
| <a class="open-in-widget" href="{{ request.path }}?sort={% ifequal sort 'timestamp' %}-{% endifequal %}timestamp">Ältere/Neuere</a>

</div>
<ol class="messages">
{% for thread in page.object_list %}
    <li>
        <span class="head">
            {% if thread.submission %}{{ thread.submission|ec_number }} - {% endif %}
            {{ thread.last_message.timestamp|naturalday:'d.m.Y' }}, {{ thread.last_message.timestamp|date:'H:i'}}
            {% if incoming %}{% trans "von" %}{% else %}{% trans "an" %}{% endif %}: <span class="user">{% block message_user %}{% endblock %}</span>
        </span>
        <span class="{% if thread.last_message.unread %}unread{% endif %}"></span>
        <a class="title open-in-popup" href="{% url ecs.communication.views.read_thread thread_pk=thread.pk %}">{{ thread.subject|truncatewords:10 }}</a>
        <span class="actions">
            {% if not incoming %}
                <a class="open-in-popup icon_bump" href="{% url ecs.communication.views.send_message bump_message_pk=thread.last_message.pk %}" title="Bump">bump</a>
            {% else %}
                <a class="open-in-popup icon_answer" href="{% url ecs.communication.views.send_message reply_to_pk=thread.last_message.pk %}" title="Antworten">answer</a>
                <a class="open-in-popup icon_delegate" href="{% url ecs.communication.views.delegate_thread thread_pk=thread.pk %}" title="Delegieren">delegate</a>
            {% endif %}
            <a class="open-in-widget icon_done" href="{% url ecs.communication.views.close_thread thread_pk=thread.pk %}?next={{ request.path|urlencode }}" title="Erledigt">done</a>
        </span>
    </li>
{% endfor %}
</ol>

<div class="paginator">
    {% block more_link %}{% endblock %}

    {% if page.has_previous %}
        <a class="open-in-widget first_page" href="{{ request.path }}?p=1">first</a>
        <a class="open-in-widget prev_page" href="{{ request.path }}?p={{ page.previous_page_number }}&amp;sort={{ sort }}">previous</a>
    {% endif %}

    {{ page.number }} von {{ page.paginator.num_pages }}
    
    {% if page.has_next %}
        <a class="open-in-widget next_page" href="{{ request.path }}?p={{ page.next_page_number }}&amp;sort={{ sort }}">next</a>
        <a class="open-in-widget last_page" href="{{ request.path }}?p={{ page.paginator.num_pages }}&amp;sort={{ sort }}">last</a>
    {% endif %}
    
</div>


