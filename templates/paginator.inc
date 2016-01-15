{% load i18n %}

<div class="paginator">
    {% if page.has_previous %}
        <a class="first_page" href="{{ request.path }}?page=1" data-page="1">first</a>
        <a class="prev_page" href="{{ request.path }}?page={{ page.previous_page_number }}" data-page="{{ page.previous_page_number }}">previous</a>
    {% endif %}
    {% trans "Page" %} {{ page.number }} {% trans "of" %} {{ page.paginator.num_pages }}
    {% if page.has_next %}
        <a class="next_page" href="{{ request.path }}?page={{ page.next_page_number }}" data-page="{{ page.next_page_number }}">next</a>
        <a class="last_page" href="{{ request.path }}?page={{ page.paginator.num_pages }}" data-page="{{ page.paginator.num_pages }}">last</a>
    {% endif %}
</div>
