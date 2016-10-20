{% load i18n tasks %}

{% if my_tasks %}
    <h3>{% trans "My Tasks" %}</h3>
    {% regroup my_tasks by task_type.workflow_node.uid as task_type_list %}
    <ul class="list-group">
        {% for task_type in task_type_list %}
            <li class="task_item list-group-item">
                <span class="tag tag-default tag-pill float-xs-right">{{ task_type.list|length }}</span>
                <h4>{{ task_type.grouper|task_type_name }}</h4>
                <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                    <a href="{{ task.url }}">{{ task.data }}</a>
                    {% if not task.accepted %}
                        <span class="fa fa-exclamation text-info" title="{% trans 'assigned' %}"></span>
                        {% if task.task_type.is_delegatable %}
                            <form class="open-in-widget" method="post" action="{% url 'ecs.tasks.views.decline_task' task_pk=task.pk %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                                {% csrf_token %}
                                <a class="submit-in-widget" href="">{% trans "Decline" %}</a>
                            </form>
                        {% endif %}
                    {% endif %}
                </li> {% endfor %} </ul>
            </li>
        {% endfor %}
    </ul>
{% endif %}

{% if proxy_tasks %}
    <h3 class="mt-1">{% trans "Proxy Tasks" %}</h3>
    {% regroup proxy_tasks by task_type.workflow_node.uid as task_type_list %}
    <ul class="list-group">
        {% for task_type in task_type_list %}
            <li class="task_item list-group-item clearfix">
                <span class="tag tag-default tag-pill float-xs-right">{{ task_type.list|length }}</span>
                <h4>{{ task_type.grouper|task_type_name }}</h4>
                <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                    <form class="open-in-widget" method="post" action="{% url 'ecs.tasks.views.accept_task' task_pk=task.pk %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                        {% csrf_token %}
                        <a class="submit-in-widget" href="">{{ task.data }}</a>
                    </form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="fa fa-search text-info" title="{% trans "Preview" %}" href="{{ preview_url }}"></a>
                        {% endif %}
                    {% endwith %}
                </li> {% endfor %} </ul>
                {% if task_type.list|length > 1 %}
                <form class="float-xs-right open-in-widget" method="post" action="{% url 'ecs.tasks.views.accept_tasks' %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                    {% csrf_token %}
                    {% for task in task_type.list %}
                        <input type="hidden" name="task_id" value="{{ task.id }}" />
                    {% endfor %}
                    <a class="submit-in-widget" href="">{% trans 'Accept all' %}</a>
                </form>
                {% endif %}
            </li>
        {% endfor %}
    </ul>
{% endif %}

<h3 class="mt-1">{% trans "Open Tasks" %}</h3>

{% if not submission %}
    <form id="{{ form_id }}" action="{{ request.path }}" method="post" class="open-in-widget">
        {% csrf_token %}
        <div class="task_list_choose">
            <label>
                {% trans "Sort by" %}
                {{ filterform.sorting }}
            </label>
        </div>
        <div class="task_list_choose">
            <label>
                {{ filterform.past_meetings }}
                {% trans "Past Meetings" %}
            </label>
            <label>
                {{ filterform.next_meeting }}
                {% trans "Next Meeting" %}
            </label>
            <label>
                {{ filterform.upcoming_meetings }}
                {% trans "Upcoming Meetings" %}
            </label>
            <label>
                {{ filterform.no_meeting }}
                {% trans "No Meeting" %}
            </label>
        </div>
        <div class="task_list_choose">
            <label>
                {{ filterform.amg }}
                <span class="fa fa-flask"></span>
                {% trans "AMG" %}
            </label>
            <label>
                {{ filterform.mpg }}
                <span class="fa fa-medkit"></span>
                {% trans "MPG" %}
            </label>
            <label>
                {{ filterform.thesis }}
                <span class="fa fa-book"></span>
                {% trans "thesis" %}
            </label>
            <label>
                {{ filterform.expedited }}
                {% trans "expedited" %}
            </label>
            <label>
                {{ filterform.local_ec }}
                {% trans "local_ec" %}
            </label>
            <label>
                {{ filterform.other }}
                <span class="fa fa-question-circle"></span>
                {% trans "Other" %}
            </label>
        </div>
    </form>
{% endif %}

{% if open_tasks %}
    {% regroup open_tasks by task_type.workflow_node.uid as task_type_list %}
    <ul class="list-group">
        {% for task_type in task_type_list %}
            <li class="task_item list-group-item clearfix">
                <span class="tag tag-default tag-pill float-xs-right">{{ task_type.list|length }}</span>
                <h4>{{ task_type.grouper|task_type_name }}</h4>
                <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                    <form class="open-in-widget" method="post" action="{% url 'ecs.tasks.views.accept_task' task_pk=task.pk %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                        {% csrf_token %}
                        <a class="submit-in-widget" href="">{{ task.data }}</a>
                    </form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="fa fa-search text-info" title="{% trans "Preview" %}" href="{{ preview_url }}"></a>
                        {% endif %}
                    {% endwith %}
                </li> {% endfor %} </ul>
                {% if task_type.list|length > 1 %}
                <form class="float-xs-right open-in-widget" method="post" action="{% url 'ecs.tasks.views.accept_tasks' %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                    {% csrf_token %}
                    {% for task in task_type.list %}
                        <input type="hidden" name="task_id" value="{{ task.id }}" />
                    {% endfor %}
                    <a class="submit-in-widget" href="">{% trans 'Accept all' %}</a>
                </form>
                {% endif %}
            </li>
        {% endfor %}
    </ul>
{% else %}
    <em>{% trans "There are no tasks for you." %}</em>
{% endif %}
