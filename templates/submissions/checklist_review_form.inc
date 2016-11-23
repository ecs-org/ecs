{% load core i18n %}

{% if not formset.readonly %}
    <form action="{{ request.path }}" method="post" class="review bound_to_task">
    {% csrf_token %}
    {{ formset.management_form }}
{% endif %}

<ol>
    {% for form in formset %}
        <li>
            {% for hidden in form.hidden_fields %}
                {{ hidden }}
            {% endfor %}
            <label for="{{ form.answer.id_for_label }}">
                {{ form.answer.label|linebreaksbr }}
            </label>
            <span class="{{ form.answer.field|type_name }}{% if form.answer.errors %} errors{% endif %}">
                {{ form.answer }}
                {% if form.answer.errors %}
                    {{ form.answer.errors }}
                {% endif %}
            </span>

            <span class="{{ form.comment.field|type_name }}{% if form.instance.question.requires_comment %} required{% endif %}{% if form.comment.errors %} errors{% endif %}">
                <label for="{{ form.comment.id_for_label }}">
                    {{ form.comment.label }}
                </label>
                {% if formset.readonly %}
                    {% url 'ecs.core.views.fieldhistory.field_history' model_name='checklist_answer' pk=form.instance.pk as history_url %}
                    <a class="fa fa-history text-primary" style="font-size:150%;" href="javascript:void(ecs.fieldhistory.show('{{ history_url }}'))"></a>
                    <br>
                {% endif %}
                {{ form.comment }}
                {% if form.comment.errors %}
                    {{ form.comment.errors }}
                {% endif %}
            </span>
        </li>
    {% endfor %}
</ol>

{% if not formset.readonly %}
    </form>
{% endif %}
