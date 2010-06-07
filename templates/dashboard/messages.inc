{% extends "dashboard/dashboard_widget.inc" %}
{% load humanize %}

{% block name %}{{ title|default:'Nachrichten' }} ({{ threads.total_message_count }}){% endblock %}

{% block content %}
<a class="popup" href="{% url ecs.messages.views.send_message %}">Neue Nachricht</a>
<table>
{% for thread in threads %}
    <tr>
        <td colspan="4">Thread: {{ thread.subject }} ({{ thread.timestamp|naturalday:'d.m.Y' }}, {{ thread.timestamp|date:'H:i'}})</td>
    </tr>
    {% for message in thread.messages.all %}
        <tr>
            <td>{% if message.unread %}<a class="unread popup" href="{% url ecs.messages.views.read_message message_pk=message.pk %}" title="ungelesen">[u]</a>{% else %}<span class="read" title="gelesen">[g]</span>{% endif %}</td>
            <td>[{{ message.sender }}]</td>
            <td>{% if message.submission %}({{ message.submission }}){% endif %}</td>
            <td><span class="reply"><a class="popup" href="{% url ecs.messages.views.send_message reply_to_pk=message.pk %}" title="antworten">Antworten</a></span></td>
        </tr>
        <tr>
            <td></td>
            <td colspan="3"><a class="popup" href="{% url ecs.messages.views.read_message message_pk=message.pk %}">{{ message.text|safe|truncatewords:10 }}</a></td>
        </tr>
    {% endfor %}

    <tr><td colspan="5">&nbsp;</td</tr>

{% endfor %}
</table>

{% endblock %}

