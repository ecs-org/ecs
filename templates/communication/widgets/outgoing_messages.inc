{% extends 'communication/widgets/messages.inc' %}

{% block title %}Warten auf{% endblock %}
{% block message_user %}{{ thread.last_message.receiver }}{% endblock %}
{% block more_link %}<a href="{% url ecs.communication.views.list_threads %}">Weitere</a>{% endblock %}

