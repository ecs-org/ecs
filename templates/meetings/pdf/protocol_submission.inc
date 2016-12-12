<div style="font-weight: bold;">Die Kommission fasst folgenden Beschluss (mit X markiert):</div>

<table class="full_width withborders">
    <tbody>
        <tr>
            <td style="width: 5%;">[X]</td>
            <td style="width: 95%;">
                {% if vote %}
                    {% include 'votes/pdf/vote_result.inc' with result=vote.result %}
                {% else %}
                    Es liegt kein Votum vor.
                {% endif %}
            </td>
        </tr>
    </tbody>
</table> 

{% if vote.text %}
    <span class="bold">Kommentar:</span><br />
    {{ vote.text|linebreaksbr }}<br />
{% endif %}

{% if submission.current_submission_form.is_amg or submission.current_submission_form.is_mpg %}
<span class="bold">
    Die Ethik-Kommission geht - rechtlich unverbindlich – davon aus, dass es sich um eine klinische Prüfung gemäß {% if submission.current_submission_form.is_amg %}AMG{% endif %}{% if submission.current_submission_form.is_amg and submission.current_submission_form.is_mpg %}/{% endif %}{% if submission.current_submission_form.is_mpg %}MPG{% endif %} handelt.
</span><br />
{% endif %}


Mitgliederliste der Ethik-Kommission (aktueller Stand am Sitzungstag) beiliegend.<br />
{% if submission.biased_board_members.count %}
Mitglieder der Ethik-Kommission, die für diesen Tagesordnungspunkt als befangen anzusehen waren und daher laut Geschäfts­ordnung an der Entscheidungsfindung/Abstimmung nicht teilgenommen haben: {% for user in submission.biased_board_members.all %}{{ user.first_name }} {{ user.last_name }}{% if not forloop.last %}, {% endif %}{% endfor %}<br />
{% endif %}
<br />
