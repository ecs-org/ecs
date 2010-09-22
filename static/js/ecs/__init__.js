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
                }
            });
            this.parent(url, options);
        }
    })
});
Element.implement(ecs.Element);
    
MooEditable.Actions.bold.title = 'Fett';
MooEditable.Actions.italic.title = 'Kursiv';
MooEditable.Actions.underline.title = 'Unterstrichen';
MooEditable.Actions.strikethrough.title = 'Durchgestrichen';
MooEditable.Actions.indent.title = 'Einrücken';
MooEditable.Actions.outdent.title = 'Ausrücken';
MooEditable.Actions.undo.title = 'Rückgängig';
MooEditable.Actions.redo.title = 'Wiederherstellen';
