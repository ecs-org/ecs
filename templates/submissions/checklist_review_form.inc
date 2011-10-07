{% load core i18n %}

{% if form.errors %}
    {{ form.errors }}
{% endif %}

{% if not review_form.readonly %}
    <form action="" method="post" class="review{% if review_form.bound_to_task %} bound_to_task{% endif %}">
{% endif %}

<ol>
  <li>
  {% for field_name in review_form.fields %}
      {% with review_form|getitem:field_name as field %}
          {% if forloop.counter0|divisibleby:2 %}
              <label for="{{ field|id_for_label }}">
                  {{ field.label|linebreaksbr }}
              </label>
              <span class="{{ field.field|type_name }}{% if field.field.required %} required{% endif %}{% if field.errors %} errors{% endif %}">
              {{ field }}
              {% if field.errors %}
                  {{ field.errors }}
              {% endif %}
              </span>
          {% else %}
              <span class="{{ field.field|type_name }}{% if field.field.required %} required{% endif %}{% if field.errors %} errors{% endif %}">
              <label for="{{ field|id_for_label }}">
                  {{ field.label }}
              </label>
              {{ field }}
              {% if field.errors %}
                  {{ field.errors }}
              {% endif %}
              </span>
              </li>
              {% if not forloop.last %}
                  <li>
              {% endif %}
          {% endif %}
      {% endwith %}
  {% endfor %}
</ol>


{% if not review_form.readonly %}
    {% if not review_form.bound_to_task %}
        <input type="submit" name="save" value="{% trans "save" %}" />
        <input style="display:none;" type="submit" name="complete_task" value="complete_task" />
        <input style="display:none;" type="submit" name="really_complete_task" value="really_complete_task" />
    {% endif %}
    </form>
{% endif %}
