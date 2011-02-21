
ecs.communication = {}


ecs.communication.Message = new Class({
    initialize: function(container){
        this.container = $(container);
        this.container.store('ecs.communication.Message', this);
        this.container.getElement('.head').addEvent('click', this.toggleCollapse.bind(this));
    },
    collapse: function(){
        this.container.addClass('collapsed');
    },
    show: function(){
        this.container.removeClass('collapsed')
    },
    toggleCollapse: function(){
        if (this.container.hasClass('collapsed')) {
            this.show();
        } else {
            this.collapse();
        }
    }
});

ecs.communication.Thread = new Class({
    initialize: function(container){
        this.container = $(container);
        this.container.store('ecs.communication.Thread', this);
        this.setup();
    },
    setup: function() {
        var messages = this.container.getElements('.message');
        var message_count = messages.length;
        var i = 0;
        messages.each(function(el){
            var message = new ecs.communication.Message(el);
            if (i < message_count -1) {
                message.collapse();
            } else {
                message.show();
            }
            i += 1;
        }, this);
    }
});

