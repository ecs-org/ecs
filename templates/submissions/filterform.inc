{% load i18n core %}

<form id="submission_list_filter" action="{{ request.path }}{% if keyword %}?keyword={{ keyword|urlencode }}{% endif %}" method="post" class="open-in-widget">
    {% csrf_token %}
    {% for row in filterform.layout %}
    <ul class="submission_list_choose">
        {% for name in row %}
            {% with filterform|get_field:name as field %}
                <li>{{ field }} <label for="id_{{ name }}"><span class="submission_{{ name }}"></span>{{ field.label }}</label></li>
            {% endwith %}
        {% endfor %}
    </ul>
    {% endfor %}
    {% if filterform.tags %}
    <ul class="submission_list_choose">
        <li>
            <label for="{{ filterform.tags.id_for_label }}">
                <span class="submission_tags">{{ filterform.tags.label }}</span>
            </label>
            {{ filterform.tags }}
        </li>
    </ul>
    {% endif %}
    {{ filterform.page }}
</form>

