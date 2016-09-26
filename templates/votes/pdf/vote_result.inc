{% load core %}

{% if result == '1' %}
    <p>Es besteht kein Einwand gegen die Durchführung der Studie.</p>
    {% get_db_setting 'vote1_extra' as extra %}
{% elif result == '2' %}
    <p>Die unten bezeichneten Punkte des Antrages sind entweder noch unerledigt
    bzw. sollten von den Antragstellern geändert/ nachgereicht werden. Nach
    entsprechender Vorlage/Erledigung kann auch vor der nächsten
    Ethik-Kommissions Sitzung ein endgültig positiver Beschluss ausgefertigt
    werden. Der Antrag wird in der nächsten Sitzung der Kommission nicht mehr
    behandelt.</p>
    {% get_db_setting 'vote2_extra' as extra %}
{% elif result == '3a' %}
    <p>Der TOP wird bis zur nächsten Sitzung vertagt.</p>
    {% get_db_setting 'vote3a_extra' as extra %}
{% elif result == '3b' %}
    <p>Es bestehen Einwände gegen die Durchführung der Studie in der
    eingereichten Form. Die unten angeführten Punkte sollten von den
    Antragstellern entsprechend geändert und der Kommission neu vorgelegt
    werden. Der Antrag wird in der nächsten Sitzung der Kommission nochmals
    behandelt.</p>
    {% get_db_setting 'vote3b_extra' as extra %}
{% elif result == '4' %}
    <p>Der Antrag wird von der Ethik-Kommission abgelehnt.</p>
    {% get_db_setting 'vote4_extra' as extra %}
{% elif result == '5' %}
    <p>Der Antrag wurde zurückgezogen.</p>
    {% get_db_setting 'vote5_extra' as extra %}
{% else %}
    <em>Unknown Vote Result {{ result }}.</em>
{% endif %}
{% if extra %}<p>{{ extra }}</p>{% endif %}
