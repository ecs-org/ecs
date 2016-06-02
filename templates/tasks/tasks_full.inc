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
    <ul class="task_list_choose">
        <li>{{ filterform.mine }} <label for="id_mine"><span class="task_mine"></span>{% trans "Mine" %}</label></li>
        <li>{{ filterform.open }} <label for="id_open"><span class="task_open"></span>{% trans "Open" %}</label></li>
        <li>{{ filterform.proxy }} <label for="id_proxy"><span class="task_proxy"></span>{% trans "Proxy" %}</label></li>
    </ul>
    <ul class="task_list_choose"{% if submission %} style="display:none"{% endif %}>
        <li>{{ filterform.past_meetings }} <label for="id_past_meetings"><span class="task_past_meetings"></span>{% trans "Past Meetings" %}</label></li>
        <li>{{ filterform.next_meeting }} <label for="id_next_meeting"><span class="task_next_meeting"></span>{% trans "Next Meeting" %}</label></li>
        <li>{{ filterform.upcoming_meetings }} <label for="id_upcoming_meetings"><span class="task_upcoming_meetings"></span>{% trans "Upcoming Meetings" %}</label></li>
        <li>{{ filterform.no_meeting }} <label for="id_no_meeting"><span class="task_no_meeting"></span>{% trans "No Meeting" %}</label></li>
    </ul>
    <ul class="task_list_choose"{% if submission %} style="display:none"{% endif %}>
        <li>{{ filterform.amg }} <label for="id_amg"><span class="task_amg"></span>{% trans "AMG" %}</label></li>
        <li>{{ filterform.mpg }} <label for="id_mpg"><span class="task_mpg"></span>{% trans "MPG" %}</label></li>
        <li>{{ filterform.thesis }} <label for="id_thesis"><span class="task_thesis"></span>{% trans "thesis" %}</label></li>
        <li>{{ filterform.expedited }} <label for="id_expedited"><span class="task_expedited"></span>{% trans "expedited" %}</label></li>
        <li>{{ filterform.local_ec }} <label for="id_local_ec"><span class="task_local_ec"></span>{% trans "local_ec" %}</label></li>
        <li>{{ filterform.other }} <label for="id_other"><span class="task_other"></span>{% trans "Other" %}</label></li>
    </ul>
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
    <div class="task_list">
        <h3>{% trans "My Tasks" %}</h3>
        {% regroup mine_tasks by task_type.workflow_node.uid as task_type_list %}
        {% for task_type in task_type_list %}
            <div class="task_item toggle_collapse">
                <h4>({{ task_type.list|length }}) {{ task_type.grouper|task_type_name }}</h4>
                <ul> {% for task in task_type.list %} <li>
                    <a href="{{ task.url }}">{{ task.data }}</a>
                    {% if not task.accepted %}
                        <span class="fa fa-exclamation text-info" title="{% trans 'assigned' %}"></span>
                        <form action="{% url 'ecs.tasks.views.decline_task_full' task_pk=task.pk %}" method="post">
                            {% csrf_token %}
                            <a class="submit_parent" href="">{% trans "Decline" %}</a>
                        </form>
                    {% endif %}
                    {% if not forloop.last %},{% endif %}
                </li> {% endfor %} </ul>
                <div style="clear:both;"></div>
            </div>
        {% endfor %}
    </div>
{% endif %}

{% if open_tasks %}
    <div class="task_list">
        <h3>{% trans "Open Tasks" %}</h3>
        {% regroup open_tasks by task_type.workflow_node.uid as task_type_list %}
        {% for task_type in task_type_list %}
            <div class="task_item toggle_collapse">
                {% if task_type.list|length > 1 %}
                <form method="post" action="{% url 'ecs.tasks.views.accept_task_type_full' flavor='open' slug=task_type.grouper %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                    {% csrf_token %}
                    <a style="float:right;padding: 0 5px;" class="submit_parent" href="">{% trans 'Accept all' %}</a>
                </form>
                {% endif %}
                <h4>({{ task_type.list|length }}) {{ task_type.grouper|task_type_name }}</h4>
                <ul> {% for task in task_type.list %} <li>
                    <form action="{% url 'ecs.tasks.views.accept_task_full' task_pk=task.pk %}" method="post"><a class="submit_parent" href="">{{ task.data }}</a>{% csrf_token %}</form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="fa fa-search text-info" title="{% trans "Preview" %}" href="{{ preview_url }}"></a>
                        {% endif %}
                    {% endwith %}
                </li> {% endfor %} </ul>
                <div style="clear:both;"></div>
            </div>
        {% endfor %}
    </div>
{% endif %}

{% if proxy_tasks %}
    <div class="task_list">
        <h3>{% trans "Proxy Tasks" %}</h3>
        {% regroup proxy_tasks by task_type.workflow_node.uid as task_type_list %}
        {% for task_type in task_type_list %}
            <div class="task_item toggle_collapse">
                {% if task_type.list|length > 1 %}
                <form method="post" action="{% url 'ecs.tasks.views.accept_task_type_full' flavor='proxy' slug=task_type.grouper %}{% if submission %}?submission={{ submission.pk }}{% endif %}">
                    {% csrf_token %}
                    <a style="float:right;padding: 0 5px;" class="submit_parent" href="">{% trans 'Accept all' %}</a>
                </form>
                {% endif %}
                <h3>({{ task_type.list|length }}) {{ task_type.grouper|task_type_name }}</h3>
                <ul> {% for task in task_type.list %} <li>
                    <form action="{% url 'ecs.tasks.views.accept_task_full' task_pk=task.pk %}" method="post"><a class="submit_parent" href="">{{ task.data }}</a>{% csrf_token %}</form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="fa fa-search text-info" title="{% trans "Preview" %}" href="{{ preview_url }}"></a>
                        {% endif %}
                    {% endwith %}
                </li> {% endfor %} </ul>
                <div style="clear:both;"></div>
            </div>
        {% endfor %}
    </div>
{% endif %}

{% if not mine_tasks and not open_tasks and not proxy_tasks %}
    <em>{% trans "There are no tasks for you." %}</em>
{% endif %}
</div>

