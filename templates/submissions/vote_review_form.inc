{% load i18n widget_tweaks %}

{% if form.errors %}
    <div class="alert alert-danger text-xs-center">
        {{ form.errors }}
    </div>
{% endif %}

{% if not review_form.readonly %}
    <form action="{{ request.path }}" method="post" class="review bound_to_task">
    {% csrf_token %}
{% endif %}

{% with review_form.text as field %}
    {% include "submissions/review_field.inc" %}
{% endwith %}
{% with review_form.is_final_version as field %}
    {% include "submissions/review_field.inc" %}
{% endwith %}

{% with review_form.result as field %}
    {% if field %}
        <div class="form-group">
            <label for="{{ field.id_for_label }}">{% trans 'Vote' %}:</label> B{{ review_form.instance.result }}
            <a onclick="$(this).hide(); $('#vote_result_change').show(); return false;">{% trans 'change' %}</a>
        </div>
        <div class="form-group {% if field.errors %}errors{% endif %}" id="vote_result_change" style="display:none;">
            {% render_field field class+="form-control" %}
            {% if field.errors %}
                <div class="alert alert-danger text-xs-center">
                    {{ field.errors }}
                </div>
            {% endif %}
        </div>
    {% endif %}
{% endwith %}

{% if not review_form.readonly %}
    </form>
{% endif %}
