<div style="font-weight: bold;">Die Kommission fasst folgenden Beschluss (mit X markiert):</div>

<table class="withborders">
    <tr>
        <td width="3%">[X]</td>
        <td>{% include 'db/meetings/wkhtml2pdf/protocol_vote.inc' %}</td>
    </tr>
</table> 

{% if vote.text %}
    <span class="bold">Kommentar:</span><br />
    {{ vote.text|linebreaksbr }}<br />
{% endif %}


Mitgliederliste der Ethik-Kommission (aktueller Stand am Sitzungstag) beiliegend.<br />
{% if submission.befangene.count %}
Mitglieder der Ethik-Kommission, die für diesen Tagesordnungspunkt als befangen anzusehen waren und daher laut Geschäfts­ordnung an der Entscheidungsfindung/Abstimmung nicht teilgenommen haben: {% for user in submission.befangene.all %}{{ user.first_name }} {{ user.last_name }}{% if not forloop.last %}, {% endif %}{% endfor %}<br />
{% endif %}
<br />
