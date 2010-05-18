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
            <td>{% if message.unread %}<span style="color:#ff0000;">[u]</span>{% else %}<span style="color:#00ff00;">[g]</span>{% endif %}</td>
            <td>[{{ message.sender }}] <a href="#" onclick="read_message('{{message.pk}}'); return false;">{{ message.subject }}</a></td>
            <td>{% if message.submission %}({{ message.submission }}){% endif %}</td>
            <td><a href="{% url ecs.messages.views.send_message reply_to_pk=message.pk %}">Re</a></td>
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

