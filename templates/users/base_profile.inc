{% load i18n %}
<table class="profile_data">
    <tr><th>Name:</th><td>{{ profile_user.first_name }} {{ profile_user.last_name }}</td></tr>
    <tr><th>E-Mail:</th><td>{{ profile_user.email }}</td></tr>
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
            <form action="{% url ecs.users.views.reset_indisposed_mark %}" method="post">
                <input type="submit" value="{% trans 'Reset' %}" />
            </form>
            {% endif %}
        </div>
    </td></tr>
    <tr><th>User-ID:</th><td>{{ profile_user.pk }}</td></tr>
</table>
