{% load i18n %}

<script type="text/javascript">
    $(function(){
        $('#{{ form_id }} select[name=task_types]').select2();

        $('#{{ form_id }}').find('select, input').change(function() {
            ecs.stopPageLoad();
            $('#{{ form_id }}').submit();
        });

        ecs.setupSubmitLinks('a.submit_parent');
    });
</script>

