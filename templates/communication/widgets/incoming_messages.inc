{% extends 'communication/widgets/messages.inc' %}

{% block title %}Empfangene/Zu beantworten{% endblock %}
{% block message_user %}{{ thread.last_message.sender }}{% endblock %}
