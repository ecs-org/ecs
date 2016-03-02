ecs.init_task_form = function() {
    var headerworkflow = $('#headerworkflow');
    var form = headerworkflow.find('form');
    var data_form = $('form.bound_to_task');

    if (data_form.length) {
        form.find('input[name=task_management-save]').show();
        form.submit(function(ev) {
            var input = form.find('input[name=task_management-post_data]');
            input.val(data_form.serialize());
        });
    }

    var toggle_headerworkflow = $('#toggle_headerworkflow');
    toggle_headerworkflow.click(function(ev) {
        ev.preventDefault();
        var visible = headerworkflow.is(':visible');
        headerworkflow.toggle();
        toggle_headerworkflow.toggleClass('collapsed', !visible);
        toggle_headerworkflow.html(visible ? '&gt;' : '&lt;');
    });
};
