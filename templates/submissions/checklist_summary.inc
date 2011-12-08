{% load core i18n userutils %}

<ol>
{% for checklist, answers in checklist_summary %}
    <li>
        <h4 class="checklist">{{ checklist.blueprint.name }}: {{ checklist.user|formal_name }}</h4>
        <ol>
        {% for answer in answers %}
            <li>
                <span class="answer">{{ answer.question.number}}. {{ answer.question.text }}: <span class="{% if answer.is_answered %}{% if answer.is_positive %}positive{% else %}negative{% endif %}{% else %}unanswered{% endif %}">{{ answer.answer|yes_no_unknown }}</span></span>
                {% if answer.comment %}
                    <span class="comment">{{ answer.comment }}</span>
                {% endif %}
            </li>

        {% endfor %}
        </ol>
    </li>
{% empty %}
    <li><em>{% trans "No Checklist yet." %}</em></li>
{% endfor %}
</ol>
