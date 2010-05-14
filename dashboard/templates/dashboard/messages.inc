{% extends "dashboard/dashboard_widget.inc" %}

{% block name %}Nachrichten ({{ message_count }}){% endblock %}

{% block content %}

<table>
{% for thread in threads %}
    <tr>
        <td colspan="6">Thread: {{ thread.subject }}</td>
    </tr>

    {% for message in thread.messages %}
        <tr>
            <td>{% if message.unread %}<span style="color:#ff0000;">[ungelesen]</span>{% else %}<span style="color:#00ff00;">[gelesen]</span>{% endif %}</td>
            <td><a href="#" onclick="read_message('{{message.pk}}'); return false;">{{ message.subject }}</a></td>
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

{% endfor %}
</table>

{% endblock %}

