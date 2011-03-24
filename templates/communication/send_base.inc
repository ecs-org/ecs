
{% if form.receiver %}
<li>
    <label for="{{ form.receiver.auto_id }}">Empfänger</label>
    {% if to_user %}
        <div class="input">
            {{ to_user }}
            <input type="hidden" name="receiver" value="{{ to_user.pk }}"/>
        </div>
    {% else %}
        <div class="input">
            {{ form.receiver_type.data }}
            <ul>
                {% for choice in form.fields.receiver_type.choices %}
                <li>
                    <label for="{{ form.receiver_type.auto_id }}_{{ forloop.counter0 }}">
                        <input id="{{ form.receiver_type.auto_id}}_{{ forloop.counter0 }}" type="radio" name="{{ form.receiver_type.html_name }}" value="{{ choice.0 }}"{% if choice.0 == form.receiver_type.data %} checked="checked"{% endif %}{% if not form.receiver_type.data and not forloop.counter0 %} checked="checked"{% endif %}>
                        {{ choice.1 }}
                    </label>
                    {% if choice.0 == "involved" %}
                        {{ form.receiver_involved }}
                        {% if form.receiver_involved.errors %}
                            <span class="errors">{{ form.receiver_involved.errors }}</span>
                        {% endif %}
                    {% endif %}
                    {% if choice.0 == "person" %}
                        {{ form.receiver_person }}
                        {% if form.receiver_person.errors %}
                            <span class="errors">{{ form.receiver_person.errors }}</span>
                        {% endif %}
                    {% endif %}
                </li>
                {% endfor %}
            </ul>
            {% if form.receiver_type.errors %}
                <span class="errors">{{ form.receiver_type.errors }}</span>
            {% endif %}
        </div>
    {% endif %}
</li>
{% endif %}

<li>
    <label for="{{ form.text.auto_id }}">Nachricht</label>
    {{ form.text }}
    {% if form.text.errors %}
        <span class="errors">{{ form.text.errors }}</span>
    {% endif %}
</li>

{% if form.non_field_errors %}
<li>
    <span class="errors">{{ form.non_field_errors }}</span>
</li>
{% endif %}

