{% load core i18n %}

{% if form.errors %}
    {{ form.errors }}
{% endif %}

{% if not review_form.readonly %}
    <form action="{{ request.path }}" method="post" class="review bound_to_task">
    {% csrf_token %}
{% endif %}

<ol>
{% with review_form.text as field %}
    {% include "submissions/review_field.inc" %}
{% endwith %}
{% with review_form.is_final_version as field %}
    {% include "submissions/review_field.inc" %}
{% endwith %}
{% with review_form.result as field %}
{% if field %}
    <li>
        <label for="{{ field.id_for_label }}">{% trans 'Vote' %}:</label> B{{ review_form.instance.result }}
        <a onclick="$(this).hide(); $('#vote_result_change').show(); return false;">{% trans 'change' %}</a>
    </li>
    <li id="vote_result_change" class="{{ field.field|type_name }}{% if field.errors %} errors{% endif %}" style="display:none;">
        {{ field }}
        {% if field.errors %}
            {{ field.errors }}
        {% endif %}
    </li>
{% endif %}
{% endwith %}
</ol>

{% if not review_form.readonly %}
    </form>
{% endif %}
