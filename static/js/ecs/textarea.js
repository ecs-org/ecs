ecs.textarea = {
    fullscreenEditor: {
        textarea: null,
        screen: null,
        sourceTextarea: null,
        toolbar: null,
        show: function(textarea) {
            if (!this.screen) {
                this.screen = $('<div/>', {'class': 'ecs-FullscreenEditor'});
                this.screen.css('display', 'none');
                this.textarea = $('<textarea/>');
                this.screen.append(this.textarea);
                this.textarea.keydown((function(ev){
                    if (ev.altKey && ev.key == 'Enter') {
                        ev.preventDefault();
                        this.sourceTextarea.val(this.textarea.val());
                        this.sourceTextarea.prop('selectionStart',
                            this.textarea.prop('selectionStart'))
                        this.sourceTextarea.prop('selectionEnd',
                            this.textarea.prop('selectionEnd'))
                        this.screen.css('display', 'none');
                        this.sourceTextarea.focus();
                    }
                }).bind(this));
                $(document.body).append(this.screen);
            }
            if (this.toolbar)
                this.toolbar.remove();
            this.sourceTextarea = textarea;
            this.textarea.val(textarea.val());
            this.textarea.prop('selectionStart', textarea.prop('selectionStart'))
            this.textarea.prop('selectionEnd', textarea.prop('selectionEnd'))
            this.toolbar = ecs.textarea.installToolbar(textarea, null, this.textarea);
            this.screen.css('display', 'block');
            this.textarea.focus();
        }
    },
    installToolbar: function(el, items, target) {
        return $(el).data('textarea').installToolbar(items, target);
    },
    installToolbarItem: function(el, item, target) {
        return $(el).data('textarea').installToolbarItem(item, target);
    }
};

ecs.textarea.TextArea = function(textarea, items, options) {
    this.textarea = $(textarea);
    this.toolbar = [];
    this.options = $.extend({
        update_height: true
    }, options);
    this.textarea.on('keydown', (function(ev) {
        if (ev.altKey && ev.key == 'Enter') {
            ev.preventDefault();
            ecs.textarea.fullscreenEditor.show(this.textarea);
        }
    }).bind(this));
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
        this.textarea.height(0).height(this.textarea.prop('scrollHeight'));
    },
    installToolbarItem: function(item, ta) {
        ta = ta || this.textarea;
        this.toolbar.push(item);
        this.toolbarElement.append(item(ta));
    },
    installToolbar: function(items, ta) {
        ta = ta || this.textarea;
        items = items || this.toolbar;
        if (!items)
            return null;

        this.toolbar = [];
        var toolbar = this.toolbarElement = $('<div/>', {'class': 'ecs-TextAreaToolbar'});
        items.forEach(function(item){
            this.installToolbarItem(item, ta);
        }, this);
        ta.before(toolbar);
        return toolbar;
    }
};
