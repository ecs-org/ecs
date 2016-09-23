{% load votes %}

{% load_vote_extra %}

{% if result == '1' %}
    <p>Es besteht kein Einwand gegen die Durchführung der Studie.</p>
    {% if vote1_extra %}<p>{{ vote1_extra }}</p>{% endif %}
{% elif result == '2' %}
    <p>Die unten bezeichneten Punkte des Antrages sind entweder noch unerledigt
    bzw. sollten von den Antragstellern geändert/ nachgereicht werden. Nach
    entsprechender Vorlage/Erledigung kann auch vor der nächsten
    Ethik-Kommissions Sitzung ein endgültig positiver Beschluss ausgefertigt
    werden. Der Antrag wird in der nächsten Sitzung der Kommission nicht mehr
    behandelt.</p>
    {% if vote2_extra %}<p>{{ vote2_extra }}</p>{% endif %}
{% elif result == '3a' %}
    <p>Der TOP wird bis zur nächsten Sitzung vertagt.</p>
    {% if vote3a_extra %}<p>{{ vote3a_extra }}</p>{% endif %}
{% elif result == '3b' %}
    <p>Es bestehen Einwände gegen die Durchführung der Studie in der
    eingereichten Form. Die unten angeführten Punkte sollten von den
    Antragstellern entsprechend geändert und der Kommission neu vorgelegt
    werden. Der Antrag wird in der nächsten Sitzung der Kommission nochmals
    behandelt.</p>
    {% if vote3b_extra %}<p>{{ vote3b_extra }}</p>{% endif %}
{% elif result == '4' %}
    <p>Der Antrag wird von der Ethik-Kommission abgelehnt.</p>
    {% if vote4_extra %}<p>{{ vote4_extra }}</p>{% endif %}
{% elif result == '5' %}
    <p>Der Antrag wurde zurückgezogen.</p>
    {% if vote5_extra %}<p>{{ vote5_extra }}</p>{% endif %}
{% else %}
    <em>Unknown Vote Result {{ result }}.</em>
{% endif %}
