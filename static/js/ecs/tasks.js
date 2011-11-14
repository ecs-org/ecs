ecs.widgets.TaskWidget = new Class({
    Implements: Events,
    initialize: function(el, options){
        options = options || {};
        this.element = $(el);
        this.element.addClass('ecs-Widget');
        this.element.store('ecs.widgets.TaskWidget', this);
        this.dataForm = $$('form.bound_to_task')[0];
        this.setup();
    },
    setup: function(){
        var self = this;
        this.element.scrollTo(0, 0);
        ecs.widgets.enablePopupHandlers(this.element, this);

        var form = this.element.getElement('form');
        if (self.dataForm) {
            form.getElement('input[name=task_management-save]').show();
        }
        var submit = function(){
            if (self.dataForm) {
                var input = form.getElement('input[name=task_management-post_data]');
                input.setAttribute('value', self.dataForm.toQueryString());
            }
            return true;
        };
        form.addEvent('submit', submit);
        // NOTE: we have to monkeypatch submit(), because the js method does not fire an onsubmit event.
        form.submit = submit;

        self.updateContentHeight();
    },
    updateContentHeight: function(){
        $('content').setStyle('top', $('header').getHeight() + 'px');
    },
    dispose: function(){
        this.element.eliminate('ecs.widgets.TaskWidget');
    }
});
