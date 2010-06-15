{% extends 'messages/widgets/messages.inc' %}

{% block title %}Neu / Zu beantworten{% endblock %}

{% block bob %}{{ message.sender }}{% endblock %}

{% block more_link %}<a href="{% url ecs.messages.views.inbox %}">Weitere</a>{% endblock %}
