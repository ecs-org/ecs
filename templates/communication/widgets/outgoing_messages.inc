{% extends 'communication/widgets/messages.inc' %}

{% block title %}Warten auf{% endblock %}
{% block message_user %}{{ thread.last_message.receiver }}{% endblock %}
