ecs.communication = {
    init_thread: function(container) {
        container = jQuery(container);

        var messages = container.find('.message');
        messages.each(function(i){
            var el = jQuery(this);

            el.find('.head').click(function(ev) {
                ev.preventDefault();
                el.toggleClass('collapsed');
            });
        });

        container.find('.collapse_all').click(function(ev){
            ev.preventDefault();
            container.find('.message').addClass('collapsed');
        });

        container.find('.expand_all').click(function(ev){
            ev.preventDefault();
            container.find('.message').removeClass('collapsed');
        });
    }
};
