
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
    initialize: function(container, collapse_link, expand_link){
        this.container = $(container);
        this.collapse_link = collapse_link ? $(collapse_link) : null;
        this.expand_link = expand_link ? $(expand_link) : null;
        this.container.store('ecs.communication.Thread', this);
        this.setup();
    },
    setup: function(){
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

        if (this.collapse_link) {
            this.collapse_link.addEvent('click', (function(){
                this.collapse_all();
                return false;
            }).bind(this));
        }
        if (this.expand_link) {
            this.expand_link.addEvent('click', (function(){
                this.expand_all();
                return false;
            }).bind(this));
        }
    },
    scroll_to_last_message: function(){
        var messages = this.container.getElements('.message');
        var last_message = messages[messages.length-1];
        var offset_parent = last_message.getOffsetParent();
        var pos = last_message.getPosition(offset_parent);
        offset_parent.scrollTo(pos.x, pos.y);
    },
    collapse_all: function(){
        var messages = this.container.getElements('.message');
        messages.each(function(el){
            var message = $(el).retrieve('ecs.communication.Message');
            message.collapse();
        }, this);
    },
    expand_all: function(){
        var messages = this.container.getElements('.message');
        messages.each(function(el){
            var message = $(el).retrieve('ecs.communication.Message');
            message.show();
        }, this);
    }
});

