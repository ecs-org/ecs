ecs.communication = {
    init_thread: function(container) {
        container = $(container);

        container.find('.message .card-header').click(function(ev) {
            var el = $(this);
            ev.preventDefault();
            el.next('.card-block').prop('hidden', function(_, val) { return !val; });
            el.find('.preview').prop('hidden', function(_, val) { return !val; });
        });

        container.find('.collapse_all').click(function(ev){
            ev.preventDefault();
            container.find('.message .card-block').prop('hidden', true);
            container.find('.message .preview').prop('hidden', false);
        });

        container.find('.expand_all').click(function(ev){
            ev.preventDefault();
            container.find('.message .card-block').prop('hidden', false);
            container.find('.message .preview').prop('hidden', true);
        });
    }
};
