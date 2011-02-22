{% extends 'communication/widgets/messages.inc' %}

{% block title %}Neu / Zu beantworten{% endblock %}
{% block message_user %}{{ thread.last_message.sender }}{% endblock %}
{% block more_link %}<a href="{% url ecs.communication.views.list_threads %}">Weitere</a>{% endblock %}

