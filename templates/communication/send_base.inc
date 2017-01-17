{% load core %}

{% if form.receiver %}
<div class="row">
    <label class="col-md-2" for="{{ form.receiver.auto_id }}" class="receiver">Empfänger</label>
    {% if to_user %}
        <div class="col-md-10 ml-3">
            {{ to_user }}
            <input type="hidden" name="receiver" value="{{ to_user.pk }}"/>
        </div>
    {% else %}
        <div class="col-md-10 col-form-label">
             {% for choice in form.fields.receiver_type.choices %}
               <div class="mb-2">
                  <label for="{{ form.receiver_type.auto_id }}_{{ forloop.counter0 }}">
                      <input id="{{ form.receiver_type.auto_id}}_{{ forloop.counter0 }}" type="radio" name="{{ form.receiver_type.html_name }}" value="{{ choice.0 }}"{% if choice.0 == form.receiver_type.data %} checked="checked"{% endif %}{% if not form.receiver_type.data and not forloop.counter0 %} checked="checked"{% endif %}>
                      {{ choice.1 }}
                  </label>
                  {% if choice.0 == "involved" %}
                      {{ form.receiver_involved }}
                      {% if form.receiver_involved.errors %}
                          <div class="errors">{{ form.receiver_involved.errors }}</div>
                      {% endif %}
                  {% endif %}
                  {% if choice.0 == "person" %}
                      {{ form.receiver_person }}
                      {% if form.receiver_person.errors %}
                          <div class="errors">{{ form.receiver_person.errors }}</div>
                      {% endif %}
                  {% endif %}
               </div>
            {% endfor %}
            {% if form.receiver_type.errors %}
                <div class="errors">{{ form.receiver_type.errors }}</div>
            {% endif %}
        </div>
    {% endif %}
</div>
{% endif %}

{% include 'bootstrap/form_field.html' with field=form.text %}

{% if form.non_field_errors %}
    <div class="alert alert-danger mt-3 mb-0" role="alert">
        {% for error in form.non_field_errors %}
            <p>{{ error }}</p>
        {% endfor %}
    </div>
{% endif %}
