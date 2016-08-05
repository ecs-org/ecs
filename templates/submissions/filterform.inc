{% load i18n core %}

<form id="submission_list_filter" action="{{ request.path }}{% if keyword %}?keyword={{ keyword|urlencode }}{% endif %}" method="post" class="open-in-widget">
    {% csrf_token %}
    {% for row in filterform.layout %}
    <div class="submission_list_choose">
        {% for name in row %}
            {% with filterform|getitem:name as field %}
                <label>
                    {{ field }}
                    {% if name == 'thesis' %}
                        <span class="fa fa-book"></span>
                    {% elif name == 'amg' %}
                        <span class="fa fa-flask"></span>
                    {% elif name == 'mpg' %}
                        <span class="fa fa-medkit"></span>
                    {% elif name == 'other' %}
                        <span class="fa fa-question-circle"></span>
                    {% endif %}
                    {{ field.label }}
                </label>
            {% endwith %}
        {% endfor %}
    </div>
    {% endfor %}
    {% if filterform.tags %}
    <div class="submission_list_choose">
        <label for="{{ filterform.tags.id_for_label }}">
            <span class="submission_tags">{{ filterform.tags.label }}</span>
        </label>
        {{ filterform.tags }}
    </div>
    {% endif %}
    {{ filterform.page }}
</form>

