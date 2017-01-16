{% load i18n widget_tweaks %}

{% if not formset.readonly %}
    <form action="{{ request.path }}" method="post" class="bound_to_task">
    {% csrf_token %}
    {{ formset.management_form }}
{% endif %}

{% for form in formset %}
    <div class="row">
        <label class="col-12" for="{{ form.answer.id_for_label }}">
            {{ form.answer.label }}
            {% if form.instance.question.requires_comment %}
                <span class="text-danger">*</span>
            {% endif %}
        </label>

        <div class="form-group col-sm-2 col-lg-1">
            {% for hidden in form.hidden_fields %}
                {{ hidden }}
            {% endfor %}
            {% render_field form.answer class+="form-control" %}
            {% if form.answer.errors %}
                {{ form.answer.errors }}
            {% endif %}
        </div>

        <div class="form-group col-sm-10 col-lg-11">
            {% if formset.readonly %}
                <div>
                    {% url 'ecs.core.views.fieldhistory.field_history' model_name='checklist_answer' pk=form.instance.pk as history_url %}
                    <a class="fa fa-2x fa-history" href="javascript:void(ecs.fieldhistory.show('{{ history_url }}'))"></a>
                </div>
            {% endif %}
            {% render_field form.comment class+="form-control" placeholder=form.comment.label %}
            {% if form.comment.errors %}
                <p class="form-text text-muted">
                    {{ form.comment.errors }}
                </p>
            {% endif %}
        </div>
    </div>
{% endfor %}

{% if not formset.readonly %}
    </form>
{% endif %}
