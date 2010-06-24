{% extends 'messages/widgets/messages.inc' %}
{% load messages %}

{% block title %}Neu / Zu beantworten{% endblock %}

{% block message_user %}{{ thread.last_message|sender_name:request.user }}{% endblock %}

{% block more_link %}<a href="{% url ecs.messages.views.inbox %}">Weitere</a>{% endblock %}
