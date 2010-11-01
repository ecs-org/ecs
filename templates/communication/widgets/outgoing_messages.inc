{% extends 'communication/widgets/messages.inc' %}
{% load communication %}

{% block title %}Warten auf{% endblock %}

{% block message_user %}{{ thread.last_message|receiver_name:request.user }}{% endblock %}

{% block more_link %}<a href="{% url ecs.communication.views.threads %}">Weitere</a>{% endblock %}
