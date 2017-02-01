{% load i18n %}
<table class="table table-sm">
    <tr><th class="bg-faded">Name:</th><td class="w-100">
        {% if profile.gender == 'f' %}Frau{% endif %}
        {% if profile.gender == 'm' %}Herr{% endif %}
        {{ profile.title }} {{ profile_user.first_name }} {{ profile_user.last_name }}
    </td></tr>
    <tr><th class="bg-faded">Organisation</th><td class="w-100">{{ profile.organisation }}</td></tr>
    <tr><th class="bg-faded">Position</th><td class="w-100">{{ profile.jobtitle }}</td></tr>
    <tr><th class="bg-faded">E-Mail</th><td class="w-100">{{ profile_user.email }}</td></tr>
    <tr><th class="bg-faded">Telefon</th><td class="w-100">{{ profile.phone }}</td></tr>
    <tr><th class="bg-faded">Fax</th><td class="w-100">{{ profile.fax }}</td></tr>
    <tr><th class="bg-faded text-nowrap">Adresse (Privatadresse falls Gutachter)</th><td class="w-100">
        {% if profile.address1 %}{{ profile.address1 }}<br/>{% endif %}
        {% if profile.address2 %}{{ profile.address2 }}<br/>{% endif %}
        {{ profile.zip_code }} {{ profile.city }}
    </td></tr>
    <tr><th class="bg-faded">Gruppen</th><td class="w-100">{% for group in profile_user.groups.all %}{{ group }}{% if not forloop.last %}, {% endif %}{% empty %}–{% endfor %}</td></tr>
    <tr><th class="bg-faded">Status</th><td class="w-100">
        <div>
            {% trans "Indisposed" %}: 
            {{ profile.is_indisposed|yesno:'ja,nein' }}
            {% if user == profile_user and profile.is_indisposed %}
                <a href="{% url 'ecs.users.views.notify_return' %}">{% trans 'Reset' %}</a>
            {% endif %}
        </div>
    </td></tr>
    <tr><th class="bg-faded">IBAN</th><td class="w-100">{{ profile.iban }}</td></tr>
    <tr><th class="bg-faded">SWIFT-BIC</th><td class="w-100">{{ profile.swift_bic }}</td></tr>
    <tr><th class="bg-faded">Sozialversicherungsnummer</th><td class="w-100">{{ profile.social_security_number }}</td></tr>
</table>
