{% load core i18n userutils %}

{% for checklist, answers in checklist_summary %}
    <div class="mb-3">
        <h4 class="checklist">
            {{ checklist.blueprint.name }}:
            {{ checklist.last_edited_by|formal_name }}
        </h4>
        {% for answer in answers %}
            <div class="ml-1 mb-1">
                {{ answer.question.number}}. {{ answer.question.text }}:
                {% if not answer.is_answered %}
                    <span class="text-muted">
                        {{ answer.answer|yes_no_unknown }}
                    </span>
                {% elif answer.is_positive %}
                    <span class="text-success">
                        {{ answer.answer|yes_no_unknown }}
                    </span>
                {% else %}
                    <span class="text-danger">
                        {{ answer.answer|yes_no_unknown }}
                    </span>
                {% endif %}
                <br>
                {% if answer.comment %}
                    <textarea class="form-control mt-1" readonly>{{ answer.comment }}</textarea>
                {% endif %}
            </div>
        {% endfor %}
    </div>
{% empty %}
    <em>
        {% trans "No Checklist with unexpected answers or unexpected comments yet." %}
    </em>
{% endfor %}
