var ecs = window.ecs = window.ecs || {};
ecs.fieldhistory = {};

ecs.fieldhistory.show = function(url){
    var modal = ecs.popup();
    modal.find('.modal-content').load(url);
};
