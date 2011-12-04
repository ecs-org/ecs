var ecs = window.ecs = window.ecs || {};
ecs.fieldhistory = {};

ecs.fieldhistory.show = function(url, field){
    var popup = new ecs.widgets.Popup({
        url: url + '?field=' + field
    });
};
