{% extends 'dashboard/messages.inc' %}

{% block title %}Warten auf{% endblock %}

{% block bob %}{{ message.receiver }}{% endblock %}

{% block more_link %}<a href="{% url ecs.messages.views.outbox %}">Weitere</a>{% endblock %}