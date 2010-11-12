ecs.textarea = {
    helper: null,
    fullscreenEditor: {
        textarea: null,
        screen: null,
        sourceTextarea: null,
        toolbar: null,
        show: function(textarea){
            if(!this.screen){
                this.screen = new Element('div', {'class': 'ecs-FullscreenEditor'});
                this.screen.setStyle('display', 'none');
                this.textarea = new Element('textarea');
                this.screen.grab(this.textarea);
                this.textarea.addEvent('keydown', (function(e){
                    if(e.alt && e.key == 'enter'){
                        this.sourceTextarea.value = this.textarea.value;
                        this.sourceTextarea.fireEvent('change');
                        this.screen.setStyle('display', 'none');
                        return false;
                    }
                }).bind(this));
                document.body.appendChild(this.screen);
            }
            if(this.toolbar){
                this.toolbar.dispose();
            }
            this.sourceTextarea = textarea;
            this.textarea.value = textarea.value;
            this.toolbar = ecs.textarea.installToolbar(textarea, null, this.textarea);
            this.screen.setStyle('display', 'block');
            this.textarea.focus();
        }
    },
    measureHeight: function(textarea, width){
        if(!this.helper){
            this.helper = new Element('div');
            this.helper.setStyles({position: 'absolute', left: '-9999px', top: '0px', 'white-space': 'pre-wrap'});
            //this.helper.setStyles({left: '800px', 'z-index': 100000, 'background-color': '#ffffff'});
            document.body.appendChild(this.helper);
        }
        this.helper.setStyle('width', width + 'px');
        this.helper.setStyles(textarea.getStyles('font-family', 'letter-spacing', 'font-size', 'font-weight', 'font-variant', 'line-height', 'padding-left', 'padding-top', 'border'));
        this.helper.innerHTML = textarea.value.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g, '<br/>') + '.';
        return this.helper.getSize().y;
    },
    installToolbar: function(el, items, target){
        return $(el).retrieve('ecs.textarea.TextArea').installToolbar(items, target);
    }
};

ecs.textarea.TextArea = new Class({
    initialize: function(textarea, options){
        options = options || {};
        this.textarea = textarea;
        this.toolbar = options.toolbar || [];
        this.updater = this.updateHeight.bind(this);
        this.textarea.addEvent('keydown', this.onKeyDown.bind(this));
        this.textarea.addEvent('keyup', this.updater);
        this.textarea.addEvent('change', this.updater);
        this.textarea.setStyle('overflow', 'hidden');
        this.interval = null;
        this.minHeight = options.minHeight || 20;
        this.updateHeight();
        this.textarea.store('ecs.textarea.TextArea', this);
    },
    updateHeight: function(){
        var h = Math.max(this.minHeight, ecs.textarea.measureHeight(this.textarea, this.textarea.getSize().x));
        this.textarea.setStyle('height', h + 'px');
    },
    onKeyDown: function(e){
        if(e.alt && e.key == 'enter'){
            ecs.textarea.fullscreenEditor.show(this.textarea);
            return false;
        }
    },
    onFocus: function(){
        this.interval = setInterval(this.updater, 333);
    },
    onBlur: function(){
        if(this.interval){
            clearInterval(this.interval);
            this.interval = null;
        }
        this.updateHeight();
    },
    installToolbar: function(items, ta){
        ta = ta || this.textarea;
        items = items || this.toolbar;
        if(!items){
            return null;
        }
        this.toolbar = items;
        var toolbar = new Element('div', {'class': 'ecs-TextAreaToolbar'});
        items.each(function(item){
            toolbar.grab(item(ta));
        });
        toolbar.inject(ta, 'before');
        return toolbar;
    }
});