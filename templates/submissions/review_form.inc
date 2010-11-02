{% load core %}

{% if form.errors %}
    {{ form.errors }}
{% endif %}

{% if not review_form.readonly %}
    <form action="" method="post" enctype="multipart/form-data" >
    {% with checklist_document_form as document_form %}
        {% with checklist_documents as documents %}
            {% include 'documents/upload_form.html' %}
        {% endwith %}
    {% endwith %}
{% endif %}
<ol>
{% for field_name in review_form.fields %}
    {% with review_form|getitem:field_name as field %}
        {% include "forms/field.html" %}
    {% endwith %}
{% endfor %}
</ol>
{% if not review_form.readonly %}
    <input type="submit" value="Speichern" />
    </form>
{% endif %}
