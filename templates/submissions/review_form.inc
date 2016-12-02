{% load core i18n %}

{% if form.errors %}
    {{ form.errors }}
{% endif %}

{% if not review_form.readonly %}
    <form action="{{ request.path }}" method="post" class="review bound_to_task">
    {% csrf_token %}
{% endif %}

{% for field_name in review_form.fields %}
    {% with review_form|getitem:field_name as field %}
        {% include "submissions/review_field.inc" %}
    {% endwith %}
{% endfor %}

{% if not review_form.readonly %}
    </form>
{% endif %}
