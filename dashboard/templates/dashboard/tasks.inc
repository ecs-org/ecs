{% extends "dashboard/dashboard_widget.inc" %}

{% block name %}Tasks{% endblock %}

{% block content %}

{% for task in tasks %}
<div>
    <h4>{{ task.task_type.name }}</h4>
    <span>Assigned to: {{ task.assigned_to }}</span>
    <span>Groups: {% for group in task.task_type.groups.all %}{{ group }}{% if not forloop.last %}, {% endif %}{% endfor %}</span>
    
</div>
{% endfor %}

{% endblock %}
