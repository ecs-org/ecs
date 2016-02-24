ecs.textarea = {
    fullscreenEditor: {
        textarea: null,
        screen: null,
        sourceTextarea: null,
        toolbar: null,
        show: function(textarea) {
            if (!this.screen) {
                this.screen = jQuery('<div/>', {'class': 'ecs-FullscreenEditor'});
                this.screen.css('display', 'none');
                this.textarea = jQuery('<textarea/>');
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
                jQuery(document.body).append(this.screen);
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
        return jQuery(el).data('textarea').installToolbar(items, target);
    },
    installToolbarItem: function(el, item, target) {
        return jQuery(el).data('textarea').installToolbarItem(item, target);
    }
};

ecs.textarea.TextArea = function(textarea, options) {
    options = options || {};
    this.textarea = jQuery(textarea);
    this.toolbar = options.toolbar || [];
    this.textarea.on('keyup change', (function(ev) {
        this.updateHeight();
    }).bind(this));
    this.textarea.on('keydown', (function(ev) {
        if (ev.altKey && ev.key == 'Enter') {
            ev.preventDefault();
            ecs.textarea.fullscreenEditor.show(this.textarea);
        }
    }).bind(this));
    this.textarea.css('overflow', 'hidden');
    this.minHeight = 20;
    this.updateHeight();
    this.textarea.data('textarea', this);
};
ecs.textarea.TextArea.prototype = {
    updateHeight: function() {
        var scroll_parent = this.textarea.parents().filter(function() {
            var parent = jQuery(this);
            return /^(auto|scroll|hidden)$/.test(parent.css('overflow-y'));
        }).eq(0);
        var scroll_top = scroll_parent.scrollTop();
        this.textarea.height('auto');
        var h = Math.max(this.minHeight, this.textarea.prop('scrollHeight'));
        this.textarea.height(h);
        scroll_parent.scrollTop(scroll_top);
    },
    installToolbarItem: function(item, ta) {
        ta = ta || this.textarea;
        this.toolbar.push(item);
        this.toolbarElement.append(item(jQuery(ta)));
    },
    installToolbar: function(items, ta) {
        ta = ta || this.textarea;
        items = items || this.toolbar;
        if (!items)
            return null;

        this.toolbar = [];
        var toolbar = this.toolbarElement = jQuery('<div/>', {'class': 'ecs-TextAreaToolbar'});
        items.each(function(item){
            this.installToolbarItem(item, ta);
        }, this);
        ta.before(toolbar);
        return toolbar;
    }
};
