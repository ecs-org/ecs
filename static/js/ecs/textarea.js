ecs.textarea = {
    installToolbar: function(el, items) {
        return $(el).data('textarea').installToolbar(items);
    },
    installToolbarItem: function(el, item) {
        return $(el).data('textarea').installToolbarItem(item);
    }
};

ecs.textarea.TextArea = function(textarea, items, options) {
    this.textarea = $(textarea);
    this.toolbar = [];
    this.options = $.extend({
        update_height: true
    }, options);
    this.textarea.data('textarea', this);
    if (items)
        this.installToolbar(items);

    if (this.options.update_height) {
        this.textarea.css({
            'overflow': 'hidden',
            'resize': 'none',
        });
        this.textarea.on('input', (function(ev) {
            this.updateHeight();
        }).bind(this));
        this.updateHeight();
    }
};
ecs.textarea.TextArea.prototype = {
    updateHeight: function() {
        var top = $(document).scrollTop();
        var padding = this.textarea.innerHeight() - this.textarea.height();
        this.textarea.height(0).height(this.textarea.prop('scrollHeight') - padding);
        $(document).scrollTop(top);
    },
    installToolbarItem: function(item) {
        this.toolbar.push(item);
        this.toolbarElement.append(item(this.textarea));
    },
    installToolbar: function(items) {
        items = items || this.toolbar;
        if (!items)
            return null;

        this.toolbar = [];
        var toolbar = this.toolbarElement = $('<div/>', {'class': 'ecs-TextAreaToolbar'});
        items.forEach(function(item){
            this.installToolbarItem(item);
        }, this);
        this.textarea.before(toolbar);
        return toolbar;
    }
};
