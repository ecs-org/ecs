{% extends 'communication/widgets/messages.inc' %}
{% load userutils %}

{% block title %}Neu / Zu beantworten{% endblock %}

{% block message_user %}{{ thread.last_message.sender|full_name }}{% endblock %}

{% block more_link %}<a href="{% url ecs.communication.views.threads %}">Weitere</a>{% endblock %}
