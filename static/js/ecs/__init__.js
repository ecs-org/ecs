if(!window.console){
    window.console = {log: $empty};
}

var ecs = window.ecs = {
    messages: new Roar({
        duration: 10000
    })
};

$extend(ecs, {
    Element: {
        setClass: function(cls, set){
            this[set ? 'addClass' : 'removeClass'](cls);
        }
    },
    Dialog: new Class({
        Extends: MooDialog.Iframe,
        initialize: function(url, options){
            $extend(options, {
                fx: {
                    type: 'tween',
                    open: 1,
                    close: 0,
                    options: {
                    duration: 0
                    }
                },
                useScrollBar: false
            });
            this.parent(url, options);
        }
    })
});
Element.implement(ecs.Element);
