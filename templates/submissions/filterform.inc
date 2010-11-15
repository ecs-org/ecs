{% load i18n %}

<form id="submission_list_filter" action="{{ request.path }}" method="post" class="open-in-widget">
    <ul class="submission_list_choose">
        {{ filterform.new }} <li><label for="id_new"><span class="submission_new"></span>{% trans "New" %}</label></li>
        {{ filterform.next_meeting }} <li><label for="id_next_meeting"><span class="submission_next_meeting"></span>{% trans "Next Meeting" %}</label></li>
        {{ filterform.b2 }} <li><label for="id_b2"><span class="submission_b2"></span>{% trans "B2 Votes" %}</label></li>
    </ul>
    <ul class="submission_list_choose">
        {{ filterform.amg }} <li><label for="id_amg"><span class="submission_amg"></span>{% trans "AMG" %}</label></li>
        {{ filterform.mpg }} <li><label for="id_mpg"><span class="submission_mpg"></span>{% trans "MPG" %}</label></li>
        {{ filterform.thesis }} <li><label for="id_thesis"><span class="submission_thesis"></span>{% trans "thesis" %}</label></li>
        {{ filterform.other }} <li><label for="id_other"><span class="submission_other"></span>{% trans "Other" %}</label></li>
    </ul>
    {{ filterform.page }}
</form>

