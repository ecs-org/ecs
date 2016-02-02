if(!window.console){
    window.console = {log: $empty};
}

var ecs = window.ecs = {
    messages: new Roar({
        duration: 10000
    })
};
