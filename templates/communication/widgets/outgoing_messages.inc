{% extends 'communication/widgets/messages.inc' %}

{% block title %}Gesendete/Warten auf{% endblock %}
{% block message_user %}{{ thread.last_message.receiver }}{% endblock %}
