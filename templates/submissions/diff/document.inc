{% load core i18n %}

<a href="{% url pdf_show doc.pk %}" target="_blank">
    {{doc.doctype}}: {{ doc.name }} (Version {{ doc.version }} vom {{ doc.date|date:'d.m.Y' }})
</a>
{% if doc.replaces_document %}
    [ersetzt <a href="{% url pdf_show doc.replaces_document.pk %}" target="_blank"">Version {{ doc.replaces_document.version }} vom {{ doc.replaces_document.date|date:'d.m.Y' }}</a>]
{% endif %}
<br />

