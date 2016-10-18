ecs.init_task_form = function() {
    var headerworkflow = $('#headerworkflow');
    var form = headerworkflow.find('form');
    var data_form = $('form.bound_to_task');

    if (data_form.length) {
        form.find('input[name=task_management-save]').removeAttr('hidden');
        form.submit(function(ev) {
            var input = form.find('input[name=task_management-post_data]');
            input.val(data_form.serialize());
        });
    }
};
