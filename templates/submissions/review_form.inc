{% load core %}

{% if not review_form.readonly %}
    <form action="" method="post">
{% endif %}
<ol>
{% for field_name in review_form.fields %}
    {% with review_form|getitem:field_name as field %}
        {% include "forms/field.html" %}
    {% endwith %}
{% endfor %}
</ol>
{% if not review_form.readonly %}
    <input type="submit" value="Speichern" />
    </form>
{% endif %}
