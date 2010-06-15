{% load humanize core %}

<h2>{% block title %}Nachrichten{% endblock %} ({{ page.paginator.count }})</h2>

<a class="widget popup" href="{% url ecs.messages.views.send_message %}">Neue Nachricht</a> 
| <a class="widget" href="{{ request.path }}?sort={% ifequal sort 'user' %}-{% endifequal %}user">Person</a> 
| <a class="widget" href="{{ request.path }}?sort={% ifequal sort 'timestamp' %}-{% endifequal %}timestamp">Ältere/Neuere</a>
<ol class="messages">
{% for message in page.object_list %}
    <li class="message {% cycle 'even' 'odd' %}{% if message.unread %} unread{% endif %}">
        <span class="head">
            {% if message.thread.submission %}{{ message.thread.submission.ec_number }} - {% endif %}
            {{ message.timestamp|naturalday:'d.m.Y' }}, {{ message.timestamp|date:'H:i'}}
        </span>
        <a class="widget popup title" href="{% url ecs.messages.views.read_message message_pk=message.pk %}">{{ message.thread.subject|truncatewords:10 }}</a>
        <span class="bob">{% block bob %}{{ message.sender }} -&gt; {{ message.receiver }}{% endblock %}</span>
        <span class="actions">
            {% if not incoming %}
                <a class="widget api" href="{% url ecs.messages.views.bump_message message_pk=message.pk %}" title="Bump"> ⟳ </a>
            {% else %}
                <a class="widget popup" href="{% url ecs.messages.views.delegate_thread thread_pk=message.thread.pk %}" title="Delegieren"> ↬ </a>
                <a class="widget popup" href="{% url ecs.messages.views.send_message reply_to_pk=message.pk %}" title="Antworten"> ➥ </a>
            {% endif %}
            <a class="widget api" href="{% url ecs.messages.views.close_thread thread_pk=message.thread.pk %}" title="Erledigt"> ✓ </a>
        </span>
    </li>
{% endfor %}
</ol>

<div class="paginator">
    {% block more_link %}{% endblock %}

    {% if page.has_previous %}
        <a class="widget" href="{{ request.path }}?p=1"> ⇤ </a>
        <a class="widget" href="{{ request.path }}?p={{ page.previous_page_number }}&amp;sort={{ sort }}"> ↩ </a>
    {% endif %}

    {% if page.has_next %}
        <a class="widget" href="{{ request.path }}?p={{ page.next_page_number }}&amp;sort={{ sort }}"> ↪ </a>
        <a class="widget" href="{{ request.path }}?p={{ page.paginator.num_pages }}&amp;sort={{ sort }}"> ⇥ </a>
    {% endif %}
    
    {{ page.number }} von {{ page.paginator.num_pages }}
</div>


