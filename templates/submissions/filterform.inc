{% load i18n core %}

<form id="submission_list_filter" action="{{ request.path }}" method="post" class="open-in-widget">
    {% for row in filterform.layout %}
    <ul class="submission_list_choose">
        {% for fname, flabel in row %}
            {{ filterform|get_field:fname }} <li><label for="id_{{ fname }}"><span class="submission_{{ fname }}"></span>{{ flabel }}</label></li>
        {% endfor %}
    </ul>
    {% endfor %}
    {{ filterform.page }}
</form>

