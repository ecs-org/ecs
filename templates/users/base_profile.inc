{% load i18n %}
<table class="profile_data">
    <tr><th>Name:</th><td>
        {% if profile.gender == 'f' %}Frau{% endif %}
        {% if profile.gender == 'm' %}Herr{% endif %}
        {{ profile.title }} {{ profile_user.first_name }} {{ profile_user.last_name }}
    </td></tr>
    <tr><th>Organisation:</th><td>{{ profile.organisation }}</td></tr>
    <tr><th>Position:</th><td>{{ profile.jobtitle }}</td></tr>
    <tr><th>E-Mail:</th><td>{{ profile_user.email }}</td></tr>
    <tr><th>Telefon:</th><td>{{ profile.phone }}</td></tr>
    <tr><th>Fax:</th><td>{{ profile.fax }}</td></tr>
    <tr><th>Adresse:</th><td>
        {{ profile.address1 }}<br/>
        {{ profile.address2 }}<br/>
        {{ profile.zip_code }} {{ profile.city }}
    </td></tr>
    <tr><th>Gruppen:</th><td>{% for group in profile_user.groups.all %}{{ group }}{% if not forloop.last %}, {% endif %}{% empty %}–{% endfor %}</td></tr>
    <tr><th>Status:</th><td>
        <div>
            EC-Office Bestätigung: 
            {% block office_approval %}{{ profile.approved_by_office|yesno:'ja,nein' }}{% endblock %}
        </div>
        <div>
            {% trans "Indisposed" %}: 
            {{ profile.indisposed|yesno:'ja,nein' }}
            {% if user == profile_user and profile.indisposed %}
                <a href="{% url ecs.users.views.toggle_indisposed user=user.pk%}">{% trans 'Reset' %}</a>
            {% endif %}
        </div>
    </td></tr>
    <tr><th>Sozialversicherungsnummer:</th><td>{{ profile.social_security_number }}</td></tr>
    <tr><th>User-ID:</th><td>{{ profile_user.pk }}</td></tr>
</table>
