{% extends 'messages/widgets/messages.inc' %}
{% load messages %}

{% block title %}Warten auf{% endblock %}

{% block message_user %}{{ message|receiver_name:request.user }}{% endblock %}

{% block more_link %}<a href="{% url ecs.messages.views.outbox %}">Weitere</a>{% endblock %}