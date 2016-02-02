if(!window.console){
    window.console = {log: function() {}};
}

var ecs = window.ecs = {
    messages: new Roar({
        duration: 10000
    })
};
