ecs.widgets = {};

ecs.widgets.Widget = new Class({
    Implements: Events,
    initialize: function(el, options){
        options = options || {};
        this.element = $(el);
        this.element.addClass('ecs-Widget');
        this.element.store('ecs.widgets.Widget', this);
        this.reload_interval = options.reload_interval;
        this.url = options.url;
        if(this.url){
            this.load();
        }
    },
    load: function(url, form, callback){
        if (this.request && this.request.running) {
            this.request.cancel();
        }
        var target_url = url;
        if(this.url && url && url.indexOf('$CURRENT_URL$') >= 0){
            url = url.replace(/\$CURRENT_URL\$/, encodeURIComponent(this.url.replace(/^https?:\/\/[^/]+/, '')));
            target_url = null; // CURRENT_URL is mainly used for redirects: do not update this.url
        }
        var request = new Request.HTML({
            url: url || (form ? form.getProperty('action') : this.url),
            method: form ? form.method : 'get',
            update: this.element,
            data: form ? form.toQueryString() : ''
        });
        if(target_url){
            this.url = target_url;
        }
        request.addEvent('success', (function(){
            if(callback){
                var stop = callback();
                if(typeof(stop) !== 'undefined' && !stop){
                    return;
                }
            }
            this.onSuccess();
        }).bind(this));
        if (this.reload_interval) {
            request.addEvent('complete', (function(){
                setTimeout((function(){
                    this.load();
                }).bind(this), this.reload_interval);
            }).bind(this));
        }
        request.send();
        this.request = request;
    },
    onSuccess: function(){
        var self = this;
        this.element.scrollTo(0, 0);
        this.element.getElements('form.open-in-widget').each(function(form){
            var submit = function(){
                self.load(null, form);
                return false;
            };
            form.addEvent('submit', submit);
            // NOTE: we have to monkeypatch submit(), because the js method does not fire an onsubmit event.
            form.submit = submit;
        });
        this.element.getElements('a.open-in-widget').each(function(link){
            link.addEvent('click', function(){
                self.load(link.href);
                return false;
            });
        });
        function submitInWidget(e){
            $(e.target).getParent('form.open-in-widget').submit();
            return false;
        }
        this.element.getElements('a.submit-in-widget').each(function(link){
            link.addEvent('click', submitInWidget);
        });
        this.fireEvent('load', this);
    },
    dispose: function(){
        this.element.eliminate('ecs.widgets.Widget');
    }
});

ecs.popup = function() {
    var modal = jQuery('\
        <div class="modal">\
            <div class="modal-dialog">\
                <div class="modal-content">\
                </div>\
            </div>\
        </div>\
    ');
    jQuery(document.body).append(modal);
    modal = jQuery(modal.get(0));
    modal.modal();
    modal.on('hidden.bs.modal', function() {
        modal.remove();
    });
    return modal;
};
