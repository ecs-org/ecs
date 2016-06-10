{% load core i18n userutils %}

<div style="display:inline-block;vertical-align:top;color:black;">
    {{doc.doctype}}: {{ doc.name }}<br />
    Version {{ doc.version }} vom {{ doc.date|date:'d.m.Y' }}
    {% if doc.replaces_document %}
        [ersetzt <a href="{% url 'ecs.core.views.submissions.view_document' submission_form_pk=submission_form.pk document_pk=doc.replaces_document.pk %}" target="_blank">Version {{ doc.replaces_document.version }} vom {{ doc.replaces_document.date|date:'d.m.Y' }}</a>]
    {% endif %}
    <br />
    {% if not plainhtml %}
    <span>
        <a href="{% url 'ecs.core.views.submissions.view_document' submission_form_pk=submission_form.pk document_pk=doc.pk %}" target="_blank">{% trans 'View' %}</a>
        {% if doc.doctype.is_downloadable or user.profile.is_internal %}
            | <a href="{% url 'ecs.core.views.submissions.download_document' submission_form_pk=submission_form.pk document_pk=doc.pk %}">{% trans "Download" %}</a>
        {% endif %}
    </span>
    {% endif %}
</div>

