{% load humanize i18n core communication %}

<h3>{% block title %}Nachrichten{% endblock %} ({{ page.paginator.count }})</h3>

<br />
<div class="messages_header">
    {% include 'communication/sort_options.inc' %}
</div>

<ol class="messages">
{% for thread in page.object_list %}
    <li>
        <span class="head">
            {% if thread.submission %}{{ thread.submission|ec_number }} - {% endif %}
            {{ thread.last_message.timestamp|naturalday:'d.m.Y' }}, {{ thread.last_message.timestamp|date:'H:i'}}
            {% if incoming %}{% trans "von" %}{% else %}{% trans "an" %}{% endif %}: <span class="user">{% block message_user %}{% endblock %}</span>
        </span>
        <span class="{% if thread.last_message.unread and thread.last_message.receiver == user %}unread{% endif %}"></span>
        <a class="title" href="{% url 'ecs.communication.views.read_thread' thread_pk=thread.pk %}" title="{{ thread.last_message|preview:80 }}">{{ thread.subject|truncatewords:10 }}</a>
        <span class="actions">
            <a class="open-in-widget fa fa-check-square-o" href="{% url 'ecs.communication.views.close_thread' thread_pk=thread.pk %}?next=$CURRENT_URL$" title="{% trans 'mark as done' %}"></a>
        </span>
    </li>
{% endfor %}
</ol>

<div class="paginator text-xs-center">
    {% if page.has_previous %}
        <a class="open-in-widget fa fa-fast-backward" href="{{ request.path }}?p=1"></a>
        <a class="open-in-widget fa fa-backward" href="{{ request.path }}?p={{ page.previous_page_number }}&amp;sort={{ sort }}"></a>
    {% endif %}
    {% trans "Page" %} {{ page.number }} {% trans "of" %} {{ page.paginator.num_pages }}
    {% if page.has_next %}
        <a class="open-in-widget fa fa-forward" href="{{ request.path }}?p={{ page.next_page_number }}&amp;sort={{ sort }}"></a>
        <a class="open-in-widget fa fa-fast-forward" href="{{ request.path }}?p={{ page.paginator.num_pages }}&amp;sort={{ sort }}"></a>
    {% endif %}
</div>
