{% load i18n %}

<div class="paginator text-xs-center my-1">
    {% if page.has_previous %}
        <a class="fa fa-fast-backward" href="{{ request.path }}?page=1" data-page="1"></a>
        <a class="fa fa-backward" href="{{ request.path }}?page={{ page.previous_page_number }}" data-page="{{ page.previous_page_number }}"></a>
    {% endif %}
    {% trans "Page" %} {{ page.number }} {% trans "of" %} {{ page.paginator.num_pages }}
    {% if page.has_next %}
        <a class="fa fa-forward" href="{{ request.path }}?page={{ page.next_page_number }}" data-page="{{ page.next_page_number }}"></a>
        <a class="fa fa-fast-forward" href="{{ request.path }}?page={{ page.paginator.num_pages }}" data-page="{{ page.paginator.num_pages }}"></a>
    {% endif %}
</div>
