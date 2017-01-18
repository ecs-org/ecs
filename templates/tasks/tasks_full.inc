{% load i18n tasks %}

<div class="card">
    <div class="card-block">
        <h3 class="card-title mb-0">{% trans "My Tasks" %}</h3>
    </div>

    {% regroup my_tasks by task_type.workflow_node.uid as task_type_list %}
    <ul class="list-group list-group-flush">
        {% for task_type in task_type_list %}
            <li class="list-group-item">
                <span class="tag tag-default tag-pill float-xs-right">{{ task_type.list|length }}</span>
                <h4>{{ task_type.grouper|task_type_name }}</h4>
                <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                    <a href="{{ task.url }}">{{ task.data }}</a>
                    {% if not task.accepted %}
                        <span class="fa fa-exclamation text-info" title="{% trans 'assigned' %}"></span>
                        {% if task.task_type.is_delegatable %}
                            <form class="d-inline-block" action="{% url 'ecs.tasks.views.decline_task_full' task_pk=task.pk %}" method="post">
                                {% csrf_token %}
                                <a class="submit_parent" href="">{% trans "Decline" %}</a>
                            </form>
                        {% endif %}
                    {% endif %}
                </li> {% endfor %} </ul>
            </li>
        {% empty %}
            <li class="list-group-item">
                <em>{% trans "There are no tasks for you." %}</em>
            </li>
        {% endfor %}
    </ul>
</div>

{% if proxy_tasks %}
    <div class="card">
        <div class="card-block">
            <h3 class="card-title mb-0">{% trans "Proxy Tasks" %}</h3>
        </div>

        {% regroup proxy_tasks by task_type.workflow_node.uid as task_type_list %}
        <ul class="list-group list-group-flush">
            {% for task_type in task_type_list %}
                <li class="list-group-item clearfix">
                    <span class="tag tag-default tag-pill float-xs-right">
                        {{ task_type.list|length }}
                    </span>
                    {% if task_type.list|length > 1 %}
                        <form class="float-xs-right mr-1" method="post" action="{% url 'ecs.tasks.views.accept_tasks_full' %}">
                            {% csrf_token %}
                            {% for task in task_type.list %}
                                <input type="hidden" name="task_id" value="{{ task.id }}" />
                            {% endfor %}
                            <a class="submit_parent" href="">
                                {% trans 'Accept all' %}
                            </a>
                        </form>
                    {% endif %}

                    <h4>{{ task_type.grouper|task_type_name }}</h4>
                    <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                        <form class="d-inline-block" action="{% url 'ecs.tasks.views.accept_task_full' task_pk=task.pk %}" method="post">
                            {% csrf_token %}
                            <a class="submit_parent" href="">{{ task.data }}</a>
                        </form>
                        {% url 'ecs.tasks.views.preview_task' task_pk=task.pk as preview_url %}
                        <a class="fa fa-search text-info" title="{% trans "Preview" %}" href="{{ preview_url }}"></a>
                    </li> {% endfor %} </ul>
                </li>
            {% endfor %}
        </ul>
    </div>
{% endif %}

{% if user.profile.can_have_open_tasks %}
    <div class="card-group">

        <div class="card no-flex-grow">
            <div class="card-block">
                <form id="{{ form_id }}" method="post">
                    {% csrf_token %}

                    <ul class="list-unstyled mb-0">
                        <li>
                            <label>
                                {{ filterform.past_meetings }}
                                {% trans "Past Meetings" %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.next_meeting }}
                                {% trans "Next Meeting" %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.upcoming_meetings }}
                                {% trans "Upcoming Meetings" %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.no_meeting }}
                                {% trans "No Meeting" %}
                            </label>
                        </li>
                    </ul>
                    <hr>
                    <ul class="list-unstyled mb-0">
                        <li>
                            <label>
                                {{ filterform.lane_board }}
                                {% trans 'board' %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.lane_expedited }}
                                {% trans 'expedited' %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.lane_retrospective_thesis }}
                                {% trans 'retrospective thesis' %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.lane_localec }}
                                {% trans 'Local EC' %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.lane_none }}
                                {% trans 'Not Categorized' %}
                            </label>
                        </li>
                    </ul>
                    <hr>
                    <ul class="list-unstyled mb-0">
                        <li>
                            <label>
                                {{ filterform.amg }}
                                {% trans "AMG" %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.mpg }}
                                {% trans "MPG" %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.thesis }}
                                {% trans "Thesis" %}
                            </label>
                        </li>
                        <li>
                            <label>
                                {{ filterform.other }}
                                {% trans "Other" %}
                            </label>
                        </li>
                    </ul>
                    <hr>
                    <label for="{{ filterform.task_types.id_for_label }}">
                        {% trans "Task Type" %}
                    </label>
                    <br>
                    {{ filterform.task_types }}
                    <hr>
                    <a class="btn btn-info btn-block" href="{{ bookmarklink }}">
                        <span class="fa fa-bookmark"></span>
                        {% trans "Bookmark" %}
                    </a>
                    <div class="mt-1">
                        <span class="fa fa-info text-info"></span>
                        {% trans "Drag the bookmark link to your bookmark bar to save it." %}
                    </div>
                </form>
            </div>
        </div>

        <div class="card">
            <div class="card-block">
                <h3 class="card-titld mb-0">{% trans "Open Tasks" %}</h3>
            </div>

            {% regroup open_tasks by task_type.workflow_node.uid as task_type_list %}
            <ul class="list-group list-group-flush">
                {% for task_type in task_type_list %}
                    <li class="list-group-item clearfix">
                        <span class="tag tag-default tag-pill float-xs-right">
                            {{ task_type.list|length }}
                        </span>
                        {% if task_type.list|length > 1 %}
                            <form class="float-xs-right mr-1" method="post" action="{% url 'ecs.tasks.views.accept_tasks_full' %}">
                                {% csrf_token %}
                                {% for task in task_type.list %}
                                    <input type="hidden" name="task_id" value="{{ task.id }}" />
                                {% endfor %}
                                <a class="submit_parent" href="">
                                    {% trans 'Accept all' %}
                                </a>
                            </form>
                        {% endif %}

                        <h4>{{ task_type.grouper|task_type_name }}</h4>
                        <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                            <form class="d-inline-block" action="{% url 'ecs.tasks.views.accept_task_full' task_pk=task.pk %}" method="post">
                                {% csrf_token %}
                                <a class="submit_parent" href="">{{ task.data }}</a>
                            </form>
                            {% url 'ecs.tasks.views.preview_task' task_pk=task.pk as preview_url %}
                            <a class="fa fa-search text-info" title="{% trans "Preview" %}" href="{{ preview_url }}"></a>
                        </li> {% endfor %} </ul>
                    </li>
                {% empty %}
                    <li class="list-group-item">
                        <em>{% trans "There are no tasks for you." %}</em>
                    </li>
                {% endfor %}
            </ul>
        </div>

    </div>
{% endif %}
