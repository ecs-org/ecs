{% load core i18n %}

{% if form.errors %}
    {{ form.errors }}
{% endif %}

{% if not review_form.readonly %}
    <form action="" method="post" class="review{% if review_form.bound_to_task %} bound_to_task{% endif %}">
{% endif %}

<ol>
{% with review_form|getitem:'text' as field %}
    {% include "submissions/review_field.inc" %}
{% endwith %}
{% with review_form|getitem:'is_final_version' as field %}
    {% include "submissions/review_field.inc" %}
{% endwith %}
{% with review_form|getitem:'result' as field %}
{% if field %}
    <li>
        <label for="{{ field|id_for_label }}">{% trans 'Vote' %}:</label> B{{ vote.result}}
        <a onclick="this.hide(); $('vote_result_change').show(); return false;">{% trans 'change' %}</a>
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
    {% if not review_form.bound_to_task %}
        <input type="submit" name="save" value="{% trans "save" %}" />
        <input style="display:none;" type="submit" name="complete_task" value="complete_task" />
        <input style="display:none;" type="submit" name="really_complete_task" value="really_complete_task" />
    {% endif %}
    </form>
{% endif %}
