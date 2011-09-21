{% load core %}

{% with field|get_field_info as field_info %}
    <li class="{{ field.field|type_name }}{% if field.field.required %} required{% endif %}{% if field.errors %} errors{% endif %}">
        {% if not readonly and field_info.help_text %}
            <span class="help_text">
                {{ field_info.help_text }}
            </span>
        {% endif %}
        <label for="{{ field|id_for_label }}">
            {% if readonly and field_info.help_text %}
                <span class="icon_comment" title="{{ field_info.help_text }}"></span>
            {% endif %}
            {{ field_info.label|default:field.label }}
            {% if field_info.number %}
                <span class="paperform_number">{{ field_info.number }}</span>
            {% endif %}
        </label>
        {{ field }}
        {% if field.errors %}
            {{ field.errors }}
        {% endif %}
    </li>
{% endwith %}
