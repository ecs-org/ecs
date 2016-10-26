{% load core widget_tweaks %}
{% with field|get_field_info as field_info %}
    {% if field.field|type_name == "BooleanField" %}
        <div class="form-check">
            {% if not readonly and field_info.help_text %}
                <span class="text-muted">
                    {{ field_info.help_text }}
                </span>
            {% endif %}
            <label class="form-check-label" for="{{ field.id_for_label }}">
                {% render_field field class+="form-check-input" %}
                {{ field_info.label|default:field.label }}
                {% if field_info.number %}
                    <small class="text-muted">{{ field_info.number }}</small>
                {% endif %}
                {% if readonly and field_info.help_text %}
                    <span class="fa fa-info text-info" title="{{ field_info.help_text }}"></span>
                {% endif %}
            </label>
        </div>
    {% else %}
        <div class="form-group{% if field.field.required %} required{% endif %}{% if field.errors %} errors{% endif %}">
            {% if not readonly and field_info.help_text %}
                <span class="text-muted">
                    {{ field_info.help_text }}
                </span>
            {% endif %}
            <label for="{{ field.id_for_label }}">
                {% if readonly and field_info.help_text %}
                    <span class="fa fa-info text-info" title="{{ field_info.help_text }}"></span>
                {% endif %}
                {{ field_info.label|default:field.label }}
                {% if field_info.number %}
                    <small class="text-muted">{{ field_info.number }}</small>
                {% endif %}
            </label>
            {% render_field field class+="form-control" %}
            {% if field.errors %}
                {{ field.errors }}
            {% endif %}
        </div>
    {% endif %}
{% endwith %}
