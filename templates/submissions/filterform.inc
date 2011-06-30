{% load i18n core %}

<form id="submission_list_filter" action="{{ request.path }}" method="post" class="open-in-widget">
    {% for row in filterform.layout %}
    <ul class="submission_list_choose">
        {% for name in row %}
            {% with filterform|get_field:name as field %}
                {{ field }} <li><label for="id_{{ name }}"><span class="submission_{{ name }}"></span>{{ field.label }}</label></li>
            {% endwith %}
        {% endfor %}
    </ul>
    {% endfor %}
    {{ filterform.page }}
</form>

