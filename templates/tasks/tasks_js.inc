{% load i18n %}

<script type="text/javascript">
    $(function(){
        $('#{{ form_id }} select[name=task_types]').select2();

        $('#{{ form_id }}').find('select, input').change(function() {
            ecs.stopPageLoad();
            $('#{{ form_id }}').submit();
        });

        var threshold = 7;

        $('#task_main .task_item').each(function() {
            var ul = $(this).find('ul');

            if (ul.find('li').length <= threshold)
                return;

            ul.find('li').slice(threshold - 1).hide();

            var li = $('<li class="list-inline-item">');
            ul.append(li);

            $('<a>{{ _('Expand')|escapejs }} &hellip;</a>')
                .appendTo(li)
                .click(function(ev) {
                    ev.preventDefault();
                    var link = $(this);
                    var lis = link.closest('ul').find('li');
                    lis.show();
                    link.remove();
                });
        });

        ecs.setupSubmitLinks('a.submit_parent');
    });
</script>

