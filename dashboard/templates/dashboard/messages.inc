{% extends "dashboard/dashboard_widget.inc" %}

{% block name %}Nachrichten ({{ message_list|length }}){% endblock %}

{% block content %}

<table>
{% for message in message_list %}
    <tr>
        <td>{% if message.unread %}<span style="color:#ff0000;">[ungelesen]</span>{% else %}<span style="color:#00ff00;">[gelesen]</span>{% endif %}</td>
        <td><a href="{% url ecs.messages.views.read_message message_pk=message.pk %}">{{ message.subject }}</a></td>
        <td>({% if message.submission %}{{ message.submission }}{% else %}Keine Einreichung{% endif %})</td>
        <td> von {{ message.sender }}</td>
        <td> gesendet am {{ message.timestamp|date:'d.m.Y, H:i:s' }} Uhr</td>
        <td><a href="{% url ecs.messages.views.send_message reply_to_pk=message.pk %}">Antworten</a></td>
    </tr>
    <tr>
        <td></td>
        <td colspan="5">{{ message.text|safe|truncatewords:10 }}</td>
    </tr>
{% endfor %}
</table>

{% endblock %}

