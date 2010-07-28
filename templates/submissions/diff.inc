{% for field, diff in diffs %}
<p>
    <div>{{ field|escape }}:</div>
    <div class="diff">
    {% for type, content in diff %}
        {% if type == 0 %}
            <span>{{ content|safe }}</span>
        {% endif %}
        {% if type == -1 %}
            <del style="color:#ff0000;">{{ content|safe }}</del>
        {% endif %}
        {% if type == 1 %}
            <ins style="color:#00ff00;">{{ content|safe }}</ins>
        {% endif %}
    {% endfor %}
    </div>
</p>
{% endfor %}

