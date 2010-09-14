{% load humanize core messages %}

<ol class="messages">
{% for thread in threads %}
    <li class="message {% cycle 'even' 'odd' %}{% if thread.last_message.unread %} unread{% endif %}">
        <h3>{{ thread.subject }} ({{ thread.sender }} &lt;-&gt; {{ thread.receiver }})</h3>
        <ol>
            {% for message in thread.messages.all %}
                <li>
                    <h4>{{ message.timestamp|naturalday:'d.m.Y' }}, {{ message.timestamp|date:'H:i'}}</h4>
                    {{ message.sender }} -&gt; {{ message.receiver }}
                    <div>
                        {{ message.text }}
                    </div>
                </li>
            {% endfor %}
        </ol>
    </li>
{% endfor %}
</ol>
