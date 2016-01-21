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
    }
});
Element.implement(ecs.Element);
