{% load i18n %}

<div id="task_main" class="task_full">
{% if submission %}
    <h1>{{ submission }}</h1>
{% endif %}

<form id="{{ form_id }}" method="post">
    <div class="task_list_choose">
        <label class="task_sorting">{% trans "Sort by" %}:</label> {{ filterform.sorting }}
    </div>
    <ul class="task_list_choose">
        <li>{{ filterform.mine }} <label for="id_mine"><span class="task_mine"></span>{% trans "Mine" %}</label></li>
        <li>{{ filterform.assigned }} <label for="id_assigned"><span class="task_assigned"></span>{% trans "Assigned" %}</label></li>
        <li>{{ filterform.open }} <label for="id_open"><span class="task_open"></span>{% trans "Open" %}</label></li>
        <li>{{ filterform.proxy }} <label for="id_proxy"><span class="task_proxy"></span>{% trans "Proxy" %}</label></li>
    </ul>
    <ul class="task_list_choose"{% if submission %} style="display:none"{% endif %}>
        <li>{{ filterform.amg }} <label for="id_amg"><span class="task_amg"></span>{% trans "AMG" %}</label></li>
        <li>{{ filterform.mpg }} <label for="id_mpg"><span class="task_mpg"></span>{% trans "MPG" %}</label></li>
        <li>{{ filterform.thesis }} <label for="id_thesis"><span class="task_thesis"></span>{% trans "thesis" %}</label></li>
        <li>{{ filterform.expedited }} <label for="id_expedited"><span class="task_expedited"></span>{% trans "expedited" %}</label></li>
        <li>{{ filterform.other }} <label for="id_other"><span class="task_other"></span>{% trans "Other" %}</label></li>
    </ul>
    <div class="task_list_choose">
        <label class="task_types">{% trans "Task Type" %}:</label> {{ filterform.task_types }}
    </div>
    <div class="task_bookmark">
        <span class="icon_comment" title="{% trans "Drag the bookmark link to your bookmark bar to save it." %}"></span> 
        <a href="{{ bookmarklink }}">{% trans "Bookmark" %}</a>
    </div>
</form>

{% if mine_tasks %}
    <div class="task_list">
        <h3>{% trans "My Tasks" %}</h3>
        {% regroup mine_tasks by task_type.trans_name as task_type_list %}
        {% for task_type in task_type_list %}
            <div class="task_item toggle_collapse">
                <h4>({{ task_type.list|length }}) {{ task_type.grouper }}</h4>
                <ul> {% for task in task_type.list %} <li>
                    <a href="{{ task.url }}" class="{% if not task.url %}open-in-popup{% endif %}">{{ task.data }}</a>{% if not forloop.last %},{% endif %}
                </li> {% endfor %} </ul>
                <div style="clear:both;"></div>
            </div>
        {% endfor %}
    </div>
{% endif %}

{% if assigned_tasks %}
    <div class="task_list">
        <h3>{% trans "Tasks assigned to me" %}</h3>
        {% regroup assigned_tasks by task_type.trans_name as task_type_list %}
        {% for task_type in task_type_list %}
            <div class="task_item toggle_collapse">
                <h4>({{ task_type.list|length }}) {{ task_type.grouper }}</h4>
                <ul> {% for task in task_type.list %} <li>
                    <form action="{% url ecs.tasks.views.accept_task_full task_pk=task.pk %}" method="post"><a class="submit_parent" href="">{{ task.data }}</a></form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="preview" title="{% trans "Preview" %}" href="{{ preview_url }}">{% trans "Preview" %}</a>
                        {% endif %}
                    {% endwith %}
                    | 
                    <form action="{% url ecs.tasks.views.decline_task_full task_pk=task.pk %}" method="post"><a class="submit_parent" href="">{% trans "Decline" %}</a></form>{% if not forloop.last %}, {% endif %}
                </li> {% endfor %} </ul>
                <div style="clear:both;"></div>
            </div>
        {% endfor %}
    </div>
{% endif %}

{% if open_tasks %}
    <div class="task_list">
        <h3>{% trans "Open Tasks" %}</h3>
        {% regroup open_tasks by task_type.trans_name as task_type_list %}
        {% for task_type in task_type_list %}
            <div class="task_item toggle_collapse">
                <h4>({{ task_type.list|length }}) {{ task_type.grouper }}</h4>
                <ul> {% for task in task_type.list %} <li>
                    <form action="{% url ecs.tasks.views.accept_task_full task_pk=task.pk %}" method="post"><a class="submit_parent" href="">{{ task.data }}</a></form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="preview" title="{% trans "Preview" %}" href="{{ preview_url }}">{% trans "Preview" %}</a>
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
        <h2>{% trans "Proxy Tasks" %}</h2>
        {% regroup proxy_tasks by task_type.trans_name as task_type_list %}
        {% for task_type in task_type_list %}
            <div class="task_item toggle_collapse">
                <h3>({{ task_type.list|length }}) {{ task_type.grouper }}</h3>
                <ul> {% for task in task_type.list %} <li>
                    <form action="{% url ecs.tasks.views.accept_task_full task_pk=task.pk %}" method="post"><a class="submit_parent" href="">{{ task.data }}</a></form>
                    {% with task.get_preview_url as preview_url %}
                        {% if preview_url %}
                            <a class="preview" title="{% trans "Preview" %}" href="{{ preview_url }}">{% trans "Preview" %}</a>
                        {% endif %}
                    {% endwith %}
                </li> {% endfor %} </ul>
                <div style="clear:both;"></div>
            </div>
        {% endfor %}
    </div>
{% endif %}

{% if not mine_tasks and not assigned_tasks and not open_tasks and not proxy_tasks %}
    <em>{% trans "There are no tasks for you." %}</em>
{% endif %}
</div>

