{% load core i18n userutils %}

{{ formset.management_form }}
<table>
{% for form in formset.forms %}
    <tr{% if not form.instance.submission.current_pending_vote %} class="text-danger"{% endif %}>
        <td>{% for hidden in form.hidden_fields %}{{ hidden }}{% endfor %}{{ form.accept_prepared_vote }}</td>
        <td>
            {% with form.instance.submission as submission %}
            {{ submission|ec_number }}: {{ submission.project_title_display }}<br>
            {% with submission.current_pending_vote as vote %}
            {% trans 'Prepared Vote' %}: {% if vote %}B{{ vote.result }}{% if vote.text %}<p>{{ vote.text|linebreaksbr }}</p>{% endif %}{% else %}<em>{% trans 'No vote!' %}</em>{% endif %}
            {% endwith %}
                {% sudo %}
                {% with submission.paper_submission_review_task as task %}
                {% if task and not task.closed_at %}
                    <div class="alert alert-danger">
                        <strong>
                            {{ task.task_type }}
                        </strong>
                        {% if task.assigned_to %}
                            ({{ task.assigned_to }})
                        {% endif %}
                    </div>
                {% endif %}
                {% endwith %}
                {% endsudo %}
            {% endwith %}
        </td>
    </tr>
{% endfor %}
</table>
