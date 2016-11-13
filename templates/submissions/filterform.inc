{% load i18n core widget_tweaks %}

<form id="submission_list_filter" action="{{ request.path }}{% if keyword %}?keyword={{ keyword|urlencode }}{% endif %}" method="post" class="form-inline open-in-widget">
    {% csrf_token %}
    {% for row in filterform.layout %}
        {% if filterform.layout|length == 1 %}
            <ul class="list-inline">
                {% for name in row %}
                    {% with filterform|getitem:name as field %}
                        <li class="list-inline-item">
                            <label>
                                {% render_field field  class+="form-control" %}
                                {{ field.label }}
                            </label>
                        </li>
                    {% endwith %}
                {% endfor %}
                </ul>
        {% else %}
                <ul class="list-unstyled">
                {% for name in row %}
                    {% with filterform|getitem:name as field %}
                        <li>
                            <label>
                                {% render_field field  class+="form-control" %}
                                {{ field.label }}
                            </label>
                        </li>
                    {% endwith %}
                {% endfor %}
                </ul>
        {% endif %}
    {% endfor %}
    {% if filterform.tags %}
        <ul class="list-unstyled pr-1 pb-1">
            <li>
                {% render_field filterform.tags class+="form-control" %}
            </li>
            {% if allow_export %}
                <li class="text-xs-right">
                    {% url 'ecs.core.views.submissions.xls_export' as export_url %}
                    <a class="btn btn-block btn-primary mt-1" href="{{ export_url }}">
                        {% trans 'Export' %} <i class="fa fa-file-excel-o"></i>
                    </a>
                </li>
            {% endif %}
        </ul>
    {% endif %}
    {{ filterform.page }}
</form>
<hr>
