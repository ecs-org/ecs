if(!window.console){
    window.console = {log: $empty};
}

var ecs = window.ecs = {
    messages: new Roar()
};

$extend(ecs, {
    Element: {
        setClass: function(cls, set){
            this[set ? 'addClass' : 'removeClass'](cls);
        }
    }
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

