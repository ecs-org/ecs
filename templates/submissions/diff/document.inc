{% load core i18n %}

<a href="{% url pdf_show doc.pk %}" target="_blank"">
    Version {{ doc.version }} vom {{ doc.date|date:'d.m.Y' }}
    {% if doc.original_file_name %}(Dateiname: {{ doc.original_file_name }}){% endif %}
</a>
{% if doc.replaces_document %}
    Ersetzt: <a href="{% url pdf_show doc.replaces_document.pk %}" target="_blank"">
        Version {{ doc.replaces_document.version }} vom {{ doc.replaces_document.date|date:'d.m.Y' }}
        {% if doc.replaces_document.original_file_name %}(Dateiname: {{ doc.replaces_document.original_file_name }}){% endif %}
    </a>
{% endif %}
<br />

