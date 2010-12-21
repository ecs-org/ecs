{% extends 'communication/widgets/messages.inc' %}
{% load userutils %}

{% block title %}Warten auf{% endblock %}

{% block message_user %}{{ thread.last_message.receiver|full_name }}{% endblock %}

{% block more_link %}<a href="{% url ecs.communication.views.threads %}">Weitere</a>{% endblock %}
