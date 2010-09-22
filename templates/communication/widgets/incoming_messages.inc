{% extends 'communication/widgets/messages.inc' %}
{% load communication %}

{% block title %}Neu / Zu beantworten{% endblock %}

{% block message_user %}{{ thread.last_message|sender_name:request.user }}{% endblock %}

{% block more_link %}<a href="{% url ecs.communication.views.inbox %}">Weitere</a>{% endblock %}
