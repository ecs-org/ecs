var ecs = window.ecs = window.ecs || {};
ecs.fieldhistory = {};

ecs.fieldhistory.show = function(url, field){
    var modal = ecs.popup();
    modal.find('.modal-content').load(url + '?field=' + field);
};
