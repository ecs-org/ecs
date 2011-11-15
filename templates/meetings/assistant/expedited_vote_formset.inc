{% load core i18n %}

{{ formset.management_form }}
<table>
{% for form in formset.forms %}
    <tr>
        <td>{% for hidden in form.hidden_fields %}{{ hidden }}{% endfor %}{{ form.accept_prepared_vote }}</td>
        <td>
            {% with form.instance.submission as submission %}
            {{ submission|ec_number }}: {{ submission.project_title_display }}<br>
            {% with submission.current_submission_form.current_vote as vote %}
            {% trans 'Prepared Vote' %}: B{{ vote.result }} {{ vote.text }}
            {% endwith %}
            {% endwith %}
        </td>
    </tr>
{% endfor %}
</table>
