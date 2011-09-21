{% if vote.result == '1' %}
    Es besteht kein Einwand gegen die Durchführung der Studie.
{% endif %}
{% if vote.result == '2' %}
    Die unten bezeichneten Punkte des Antrages sind entweder noch unerledigt bzw sollten von den Antragstellern geändert/ nachgereicht werden.
    Nach entsprechender Vorlage/Erledigung kann auch vor der nächsten Ethik-Kommissions Sitzung ein endgültig positiver Beschluß ausgefertigt werden.
    Der Antrag wird in der nächsten Sitzung der Kommission nicht mehr behandelt.<br/>
    <div style="font-size: small;">
        <span style="text-decoration: underline;">Achtung:</span>
        Werden die geforderten Unterlagen von den Antragstellern nicht innerhalb von 3 Sitzungsperioden (ab Datum dieser Sitzung) nachgereicht,
        gilt der Antrag ohne weitere Benachrichtigung als zurückgezogen und muß gegebenenfalls als Neuantrag eingereicht werden.
    </div>
{% endif %}
{% if vote.result == '3a' %}
    Der TOP wird bis zur nächsten Sitzung vertagt.
{% endif %}
{% if vote.result == '3b' %}
    Es bestehen Einwände gegen die Durchführung der Studie in der eingereichten Form.
    Die unten angeführten Punkte sollten von den Antragstellern entsprechend geändert und der Kommission neu vorgelegt werden.
    Der Antrag wird in der nächsten Sitzung der Kommission nochmals behandelt. <br/>
    <div style="font-size: small;">
        <span style="text-decoration: underline;">Achtung:</span>
        Werden die geforderten Unterlagen von den Antragstellern nicht innerhalb von 3 Sitzungsperioden (ab Datum dieser Sitzung) nachgereicht,
        gilt der Antrag ohne weitere Benachrichtigung als zurückgezogen und muß gegebenenfalls als Neuantrag eingereicht werden.
    </div>
{% endif %}
{% if vote.result == '4' %}
    Der Antrag wird von der Ethik-Kommission abgelehnt.
{% endif %}
{% if vote.result == '5' %}
    Der Antrag wurde vom Antragsteller zurückgezogen.
{% endif %}
{% if not vote %}
    Es liegt kein Votum vor.
{% endif %}
