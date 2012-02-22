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
{% empty %}
<div style="margin:20px;">
    <em>{% trans 'No messages yet!' %}</em>
</div>
{% endfor %}

<div>
    <span class="icon_comment"></span>
    {% if show_system_messages %}
        {% trans 'System messages are shown.' %}
        <a href="{{ request.path }}" class="open-in-widget">{% trans 'Hide system messages' %}</a>
    {% else %}
        {% trans 'System messages are hidden.' %}
        <a href="{{ request.path }}?show_system_messages=show_system_messages" class="open-in-widget">{% trans 'Show system messages' %}</a>
    {% endif %}
</div>

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

