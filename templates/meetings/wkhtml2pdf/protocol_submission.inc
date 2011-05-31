<div style="font-weight: bold;">Die Kommission fasst folgenden Beschluss (mit X markiert):</div>

<table class="withborders">
    <tr>
        <td width="3%">[X]</td>
        <td>{% include 'db/meetings/wkhtml2pdf/protocol_vote.inc' %}</td>
    </tr>
</table> 

{% if vote.text %}
    <span class="bold">Kommentar:</span><br />
    {{ vote.text|escape}}
{% endif %}

{% if submission.is_mpg %}
    <span class="bold">Die Ethik-Kommission geht - rechtlich unverbindlich – davon aus, daß es sich um eine klinische Prüfung gemäß MPG handelt</span><br />
{% endif %}
{% if submission.is_amg %}
    <span class="bold">Die Ethik-Kommission geht - rechtlich unverbindlich – davon aus, daß es sich um eine klinische Prüfung gemäß AMG handelt</span><br />
{% endif %}
{% if not submission.is_mpg and not submission.is_amg %}
    <span class="bold">Die Ethik-Kommission geht - rechtlich unverbindlich – davon aus, daß es sich um keine klinische Prüfung gemäß AMG/MPG handelt</span><br />
{% endif %}


Mitgliederliste der Ethik-Kommission (aktueller Stand am Sitzungstag) beiliegend.<br />
{% if submission.befangene.count %}
Mitglieder der Ethik-Kommission, die für diesen Tagesordnungspunkt als befangen anzusehen waren und daher laut Geschäfts­ordnung an der Entscheidungsfindung/Abstimmung nicht teilgenommen haben: {% for user in submission.befangene.all %}{{ user.first_name }} {{ user.last_name }}{% if not forloop.last %}, {% endif %}{% endfor %}<br />
{% endif %}
<br />
