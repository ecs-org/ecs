{% load core i18n %}

{{ formset.management_form }}
<table>
{% for form in formset.forms %}
    <tr{% if not form.instance.submission.current_submission_form.current_vote %} style="color:red;"{% endif %}>
        <td>{% for hidden in form.hidden_fields %}{{ hidden }}{% endfor %}{{ form.accept_prepared_vote }}</td>
        <td>
            {% with form.instance.submission as submission %}
            {{ submission|ec_number }}: {{ submission.project_title_display }}<br>
            {% with submission.current_submission_form.current_vote as vote %}
            {% trans 'Prepared Vote' %}: {% if vote %}B{{ vote.result }}{% if vote.text %}<p>{{ vote.text|linebreaksbr }}</p>{% endif %}{% else %}<em>{% trans 'No vote!' %}</em>{% endif %}
            {% endwith %}
            {% endwith %}
        </td>
    </tr>
{% endfor %}
</table>
