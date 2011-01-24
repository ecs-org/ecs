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
                        this.sourceTextarea.focus();
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
    measureHeight: function(textarea){
        if(!this.measure_helper){
            this.measure_helper = new Element('div');
            this.measure_helper.setStyles({position: 'absolute', left: '-9999px', top: '0px', 'white-space': 'pre-wrap', 'word-wrap': 'break-word'});
            //this.measure_helper.setStyles({left: '800px', 'z-index': 100000, 'background-color': '#ffffff'});
            document.body.appendChild(this.measure_helper);
        }
        if(!this.width_helper){
            this.width_helper = new Element('div');
            this.width_helper.setStyles({position: 'absolute', left: '-9999px', top: '0px'});
            document.body.appendChild(this.width_helper);
        }
        if(!textarea.isVisible()){
            var textarea_copy = textarea.clone();
            textarea_copy.inject(this.width_helper);
            var width = textarea_copy.getStyle('width');
            textarea_copy.dispose();
        } else {
            var width = textarea.getStyle('width');
        }
        this.measure_helper.setStyles(textarea.getStyles('font-family', 'letter-spacing', 'font-size', 'font-weight', 'font-variant', 'line-height', 'padding-left', 'padding-top', 'border'));
        this.measure_helper.setStyle('width', width);
        this.measure_helper.innerHTML = textarea.value.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g, '<br/>') + '.';
        return this.measure_helper.getSize().y;
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
        var h = Math.max(this.minHeight, ecs.textarea.measureHeight(this.textarea));
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
