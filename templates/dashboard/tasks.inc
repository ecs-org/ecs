{% extends "dashboard/dashboard_widget.inc" %}

{% block name %}Tasks{% endblock %}

{% block content %}

{% if accepted_tasks %}
    <div class="TaskList">
        <h2>Meine Tasks</h2>
        {% for task in accepted_tasks %}
        <div>
            <a class="popup" href="{% url ecs.tasks.views.manage_task task_pk=task.pk %}">{{ task }}</a>
            <span class="actions">
                <a class="popup" href="{% url ecs.tasks.views.delegate_task task_pk=task.pk %}" class="">Delegieren</a> 
            </span>
        </div>
        {% endfor %}
    </div>
{% endif %}
{% if assigned_tasks %}
    <div class="TaskList">
        <h2>Mir zugewiesene Tasks</h2>
        {% for task in assigned_tasks %}
        <div>
            {{ task }}
            <span class="actions">
                <a href="{% url ecs.tasks.views.accept_task task_pk=task.pk %}?next={{ request.path }}">Annehmen</a> 
                | <a href="{% url ecs.tasks.views.decline_task task_pk=task.pk %}?next={{ request.path }}">Ablehnen</a>
            </span>
        </div>
        {% endfor %}
    </div>
{% endif %}
{% if open_tasks %}
    <div class="TaskList">
        <h2>Offene Tasks</h2>
        {% for task in open_tasks %}
        <div>
            {{ task }}
            <span class="actions">
                <a href="{% url ecs.tasks.views.accept_task task_pk=task.pk %}?next={{ request.path }}">Annehmen</a> 
                | <a class="popup" href="{% url ecs.tasks.views.delegate_task task_pk=task.pk %}">Delegieren</a>
            </span>
        </div>
        {% endfor %}
    </div>
{% endif %}

{% endblock %}
