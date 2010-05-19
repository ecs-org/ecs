{% extends "dashboard/dashboard_widget.inc" %}
{% load humanize %}

{% block name %}Nachrichten ({{ message_count }}){% endblock %}

{% block content %}

<table>
{% for thread in threads %}

    {% with thread.messages.0 as first_message %}
        <tr>
            <td colspan="4">Thread: {{ thread.subject }} ({{ first_message.timestamp|naturalday:'d.m.Y' }}, {{ first_message.timestamp|date:'H:i'}})</td>
        </tr>
    {% endwith %}

    {% for message in thread.messages %}
        <tr>
            <td>{% if message.unread %}<span class="unread">[u]</span>{% else %}<span class="read">[g]</span>{% endif %}</td>
            <td>[{{ message.sender }}] <a class="popup" href="{% url ecs.messages.views.read_message message_pk=message.pk %}">{{ message.subject }}</a></td>
            <td>{% if message.submission %}({{ message.submission }}){% endif %}</td>
            <td><span class="reply"><a class="popup" href="{% url ecs.messages.views.send_message reply_to_pk=message.pk %}" title="antworten">Antworten</a></span></td>
        </tr>
        <tr>
            <td></td>
            <td colspan="3">{{ message.text|safe|truncatewords:10 }}</td>
        </tr>
    {% endfor %}

    <tr><td colspan="5">&nbsp;</td</tr>

{% endfor %}
</table>

{% endblock %}

