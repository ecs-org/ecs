{% load i18n tasks %}

<div id="task_main" class="task_full">
{% if submission %}
    <h1>{{ submission }}</h1>
{% endif %}

<form id="{{ form_id }}" method="post">
    {% csrf_token %}
    <div class="task_list_choose">
        <label class="task_sorting">{% trans "Sort by" %}:</label> {{ filterform.sorting }}
    </div>
    <div class="task_list_choose">
        <label>
            {{ filterform.mine }}
            <span class="fa fa-user"></span>
            {% trans "Mine" %}
        </label>
        <label>
            {{ filterform.open }}
            <span class="fa fa-users"></span>
            {% trans "Open" %}
        </label>
        <label>
            {{ filterform.proxy }}
            <span class="fa fa-user-times"></span>
            {% trans "Proxy" %}
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
    <div class="task_list_choose"{% if submission %} style="display:none"{% endif %}>
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
    <div class="task_list_choose task_select">
        <label class="task_types">{% trans "Task Type" %}:</label> {{ filterform.task_types }}
    </div>
    <div class="task_bookmark" title="{% trans "Drag the bookmark link to your bookmark bar to save it." %}">
        <a href="{{ bookmarklink }}">
            <span class="fa fa-bookmark text-primary"></span>
            {% trans "Bookmark" %}
        </a>
    </div>
</form>

{% if mine_tasks %}
    <h3 class="m-t-1">{% trans "My Tasks" %}</h3>
    {% regroup mine_tasks by task_type.workflow_node.uid as task_type_list %}
    <ul class="list-group">
        {% for task_type in task_type_list %}
            <li class="task_item list-group-item">
                <span class="tag tag-default tag-pill pull-xs-right">{{ task_type.list|length }}</span>
                <h4>{{ task_type.grouper|task_type_name }}</h4>
                <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                    <a href="{{ task.url }}">{{ task.data }}</a>
                    {% if not task.accepted %}
                        <span class="fa fa-exclamation text-info" title="{% trans 'assigned' %}"></span>
                        {% if task.task_type.is_delegatable %}
                            <form action="{% url 'ecs.tasks.views.decline_task_full' task_pk=task.pk %}" method="post">
                                {% csrf_token %}
                                <a class="submit_parent" href="">{% trans "Decline" %}</a>
                            </form>
                        {% endif %}
                    {% endif %}
                    {% if not forloop.last %},{% endif %}
                </li> {% endfor %} </ul>
            </li>
        {% endfor %}
    </ul>
{% endif %}

{% if open_tasks %}
    <h3 class="m-t-1">{% trans "Open Tasks" %}</h3>
    {% regroup open_tasks by task_type.workflow_node.uid as task_type_list %}
    <ul class="list-group">
        {% for task_type in task_type_list %}
            <li class="task_item list-group-item clearfix">
                <span class="tag tag-default tag-pill pull-xs-right">{{ task_type.list|length }}</span>
                <h4>{{ task_type.grouper|task_type_name }}</h4>
                <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                    <form action="{% url 'ecs.tasks.views.accept_task_full' task_pk=task.pk %}" method="post"><a class="submit_parent" href="">{{ task.data }}</a>{% csrf_token %}</form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="fa fa-search text-info" title="{% trans "Preview" %}" href="{{ preview_url }}"></a>
                        {% endif %}
                    {% endwith %}
                </li> {% endfor %} </ul>
                {% if task_type.list|length > 1 %}
                <form class="pull-xs-right" method="post" action="{% url 'ecs.tasks.views.accept_task_type_full' flavor='open' slug=task_type.grouper %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                    {% csrf_token %}
                    <a class="submit_parent" href="">{% trans 'Accept all' %}</a>
                </form>
                {% endif %}
            </li>
        {% endfor %}
    </ul>
{% endif %}

{% if proxy_tasks %}
    <h3 class="m-t-1">{% trans "Proxy Tasks" %}</h3>
    {% regroup proxy_tasks by task_type.workflow_node.uid as task_type_list %}
    <ul class="list-group">
        {% for task_type in task_type_list %}
            <li class="task_item list-group-item clearfix">
                <span class="tag tag-default tag-pill pull-xs-right">{{ task_type.list|length }}</span>
                <h4>{{ task_type.grouper|task_type_name }}</h4>
                <ul class="list-inline"> {% for task in task_type.list %} <li class="list-inline-item">
                    <form action="{% url 'ecs.tasks.views.accept_task_full' task_pk=task.pk %}" method="post"><a class="submit_parent" href="">{{ task.data }}</a>{% csrf_token %}</form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="fa fa-search text-info" title="{% trans "Preview" %}" href="{{ preview_url }}"></a>
                        {% endif %}
                    {% endwith %}
                </li> {% endfor %} </ul>
                {% if task_type.list|length > 1 %}
                <form class="pull-xs-right" method="post" action="{% url 'ecs.tasks.views.accept_task_type_full' flavor='proxy' slug=task_type.grouper %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                    {% csrf_token %}
                    <a class="submit_parent" href="">{% trans 'Accept all' %}</a>
                </form>
                {% endif %}
            </li>
        {% endfor %}
    </ul>
{% endif %}

{% if not mine_tasks and not open_tasks and not proxy_tasks %}
    <em>{% trans "There are no tasks for you." %}</em>
{% endif %}
</div>

