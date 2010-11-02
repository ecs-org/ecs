{% load i18n %}

<form id="submission_list_filter" action="" method="post">
    <div class="submission_list_choose">
        {{ filterform.new }} <label for="id_new" class="submission_new">{% trans "New" %}</label>
        {{ filterform.next_meeting }} <label for="id_next_meeting" class="submission_next_meeting">{% trans "Next Meeting" %}</label>
        {{ filterform.b2 }} <label for="id_b2" class="submission_b2">{% trans "B2 Votes" %}</label>
    </div>
    <div class="submission_list_choose">
        {{ filterform.amg }} <label for="id_amg" class="submission_amg">{% trans "AMG" %}</label>
        {{ filterform.mpg }} <label for="id_mpg" class="submission_mpg">{% trans "MPG" %}</label>
        {{ filterform.thesis }} <label for="id_thesis" class="submission_thesis">{% trans "thesis" %}</label>
        {{ filterform.other }} <label for="id_other" class="submission_other">{% trans "Other" %}</label>
    </div>
    {{ filterform.page }}
</form>

