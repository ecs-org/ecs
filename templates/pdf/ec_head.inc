{% load core corepdf %}

<div class="header">
    <img class="logo" src="{% print_logo_url %}" alt="Logo" />

    <div class="address">
        {% db_setting 'address' as address %}

        {{ address|linebreaksbr }}<br>
        {% db_setting 'contact_email' %}<br>
        {% db_setting 'contact_url' %}
    </div>

    <div class="spacer">&nbsp;</div>
</div>
