{% load core i18n userutils %}

<ol>
{% for checklist, answers in checklist_summary %}
    <li>
        <div class="checklist">{{ checklist.blueprint.name }}: {{ checklist.user|formal_name }}</div>
        <ol>
        {% for answer in answers %}
            <li>
                <div class="answer">{{ answer.question.number}}. {{ answer.question.text }}: <span class="{% if answer.is_answered %}{% if answer.is_positive %}positive{% else %}negative{% endif %}{% else %}unanswered{% endif %}">{{ answer.answer|yes_no_unknown }}</span></div>
                {% if answer.comment %}
                    <div class="comment">{{ answer.comment }}</div>
                {% endif %}
            </li>

        {% endfor %}
        </ol>
    </li>
{% empty %}
    <li><em>{% trans "No Checklist yet." %}</em></li>
{% endfor %}
</ol>
