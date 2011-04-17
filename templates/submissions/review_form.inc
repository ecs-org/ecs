{% load core %}

{% if form.errors %}
    {{ form.errors }}
{% endif %}

{% if not review_form.readonly %}
    <form action="" method="post" class="review">
{% endif %}

<ol>
{% for field_name in review_form.fields %}
    {% with review_form|getitem:field_name as field %}
        {% include "forms/field.html" %}
    {% endwith %}
{% endfor %}
</ol>
{% if not review_form.readonly %}
    <input type="submit" name="save" value="save" />
    <input style="display:none;" type="submit" name="complete_task" value="complete_task" />
    <input style="display:none;" type="submit" name="really_complete_task" value="really_complete_task" />
    </form>
{% endif %}
