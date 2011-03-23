{% load humanize core communication %}

{% for thread in threads %}
<div class="communication_thread">
    <h3>{{ thread.subject }} ({{ thread.sender }} &lt;-&gt; {{ thread.receiver }})</h3>

    <ul class="thread">
    {% for message in thread.message_list %}
        <li class="message">
            <div class="head">
                <span class="sender">{{ message.sender }}</span>
                <span class="preview">{{ message|preview:80 }}</span>
                <span class="time">{{ message.timestamp|date:'d.m.Y H:i' }} Uhr</span>
            </div>
            <pre class="body">{{ message.text|safe }}<pre>
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

