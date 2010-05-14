{% extends "dashboard/dashboard_widget.inc" %}

{% block name %}Tasks{% endblock %}

{% block content %}

{% for task in tasks %}
<div>
    <span>{{ task.task_type.name }}</span>
    <span>Assigned to: {{ task.assigned_to }}</span>
    <span>Groups: {% for group in task.task_type.groups.all %}{{ group }}{% if not forloop.last %}, {% endif %}{% endfor %}</span>
    
</div>
{% endfor %}

{% endblock %}
