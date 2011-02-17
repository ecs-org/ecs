
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
            {{ form.receiver_type }}
            {% if form.receiver_type.errors %}
                <span class="errors">{{ form.receiver_type.errors }}</span>
            {% endif %}

            {{ form.receiver_involved }}
            {% if form.receiver_involved.errors %}
                <span class="errors">{{ form.receiver_involved.errors }}</span>
            {% endif %}

            {{ form.receiver_person }}
            {% if form.receiver_person.errors %}
                <span class="errors">{{ form.receiver_person.errors }}</span>
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

