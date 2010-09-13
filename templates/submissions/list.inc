<ol class="submission_list">
{% for submission in submissions %}
    <li class="{% cycle 'even' 'odd' %}">
        <h3><span class="ecnr">{{ submission.ec_number }}</span> {{ submission.project_title|default:'<i>Ohne Titel</i>' }}</h3>
        <div class="actions">
            <a href="{% url ecs.core.views.copy_latest_submission_form submission_pk=submission.pk %}">Bearbeiten</a>
             | <a href="{% url ecs.core.views.schedule_submission submission_pk=submission.pk %}">Schedule</a>
             <!--| <a href="{% url ecs.core.views.start_workflow submission_pk=submission.pk %}">Start Workflow</a>-->
             {% with submission.get_most_recent_form as submission_form %}
                 {% if submission_form %}
                     | <a href="{% url ecs.core.views.readonly_submission_form submission_form_pk=submission_form.pk %}">Ansehen</a>
                     | <a href="{% url ecs.core.views.submission_pdf submission_form_pk=submission_form.pk %}">Download PDF</a>
                     <!--| <a href="{% url ecs.core.views.copy_submission_form submission_form_pk=submission_form.pk %}">Copy</a>-->
                     | <a href="{% url ecs.core.views.executive_review submission_form_pk=submission_form.pk %}">Executive Review</a>
                     | <a href="{% url ecs.core.views.retrospective_thesis_review submission_form_pk=submission_form.pk %}">Thesis Review</a>
                     | <a href="{% url ecs.core.views.checklist_review submission_form_pk=submission_form.pk blueprint_pk=1 %}">Statistik Review</a>
                     | <a href="{% url ecs.core.views.befangene_review submission_form_pk=submission_form.pk %}">Befangene Review</a>
                     {% with submission.get_most_recent_vote as vote %}
                        {% if vote %}
                            | <a href="{% url ecs.core.views.vote_review submission_form_pk=submission_form.pk %}">Vote Review</a>
                            {% if vote.result == '2' %}
                                | <a href="{% url ecs.core.views.b2_vote_review submission_form_pk=submission_form.pk %}">B2 Vote Review</a>
                            {% endif %}
                        {% endif %}
                     {% endwith %}
                 {% endif %}
             {% endwith %}
             | <a href="{% url ecs.core.views.export_submission submission_pk=submission.pk %}">Export</a>
        </div>
        {% with submission.medical_categories.all as categories %}
            {% if categories %}
                <div class="info">Kategorien: {% for cat in categories %}<i>{{ cat }}</i>{% if not forloop.last %}, {% endif %}{% endfor %}</div>
            {% endif %}
        {% endwith %}
        {% with submission.expedited_review_categories.all as er_categories %}
            {% if categories %}
                <div class="info">ExpeditedReviewCategories: {% for cat in categories %}<i>{{ cat }}</i>{% if not forloop.last %}, {% endif %}{% endfor %}</div>
            {% endif %}
        {% endwith %}
        {% with submission.meetings.distinct as meetings %}
            {% if meetings %}
                <div class="info">Sitzungen: {% for meeting in meetings %}<a href="{% url ecs.core.views.timetable_editor meeting_pk=meeting.pk %}">{{ meeting.start|date:'d.m.Y' }} ({{ meeting.title }})</a>{% if not forloop.last %}, {% endif %}{% endfor %}</div>
            {% endif %}
        {% endwith %}
    </li>
{% endfor %}
</ol>
