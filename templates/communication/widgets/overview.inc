{% load humanize core communication i18n %}

{% for thread in threads %}
<div class="communication_thread">
    <h3>{{ thread.subject }} ({{ thread.sender }} &lt;-&gt; {{ thread.receiver }})</h3>

    <ul class="thread">
    {% for message in thread.message_list %}
        <li class="message">
            <div class="head">
                <span class="sender">{% if message.sender == user %}{% trans 'Me' %}{% else %}{{ message.sender }}{% endif %}</span>
                <span class="preview"></span><span class="preview_text">{{ message|preview:80 }}</span>
                <span class="time">{{ message.timestamp|naturalday:'d.m.Y' }} {{ message.timestamp|date:'H:i' }} Uhr</span>
            </div>
            <pre class="body">{{ message.text|urlize }}</pre>
        </li>
    {% endfor %}
    </ul>
</div>
{% endfor %}

<script type="text/javascript">
    window.addEvent('domready', function(){
        var threads = $$('.communication_thread');
        threads.each(function(el){
            var container = el.getElement('ul');
            var thread = new ecs.communication.Thread(container);
            thread.collapse_all();
        }, this);
    });
</script>

