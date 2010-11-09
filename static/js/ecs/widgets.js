ecs.widgets = {
    modalOverlay: null,
    getWidgetForElement: function(el){
        var parent = $(el).getParent('.ecs-Widget');
        if(!parent){
            return null;
        }
        return parent.retrieve('ecs.widgets.Widget');
    },
    showModalOverlay: function(){
        if(!this.modalOverlay){
            this.modalOverlay = new Element('div', {'class': 'ecs-ModalOverlay', style: 'display:none'});
            document.body.appendChild(this.modalOverlay);
        }
        this.modalOverlay.setStyle('display', 'block');
    },
    hideModalOverlay: function(){
        if(this.modalOverlay){
            this.modalOverlay.setStyle('display', 'none');
        }
    }
};

ecs.widgets.Widget = new Class({
    Implements: Events,
    initialize: function(el, options){
        options = options || {};
        this.element = $(el);
        this.element.addClass('ecs-Widget');
        this.element.store('ecs.widgets.Widget', this);
        this.url = options.url;
        if(this.url){
            this.load();
        }
    },
    load: function(url, form){
        var request = new Request.HTML({
            url: url || (form && form.action) || this.url,
            method: form ? form.method : 'get',
            update: this.element,
            data: form ? form.toQueryString() : ''
        });
        if(url){
            this.url = url;
        }
        request.addEvent('success', this.onSuccess.bind(this));
        request.send();
    },
    onSuccess: function(){
        var self = this;
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
        this.fireEvent('load', this);
    },
    dispose: function(){
        this.element.eliminate('ecs.widgets.Widget');
    }
});

ecs.widgets.Popup = new Class({
    Extends: ecs.widgets.Widget,
    initialize: function(options){
        options = options || {};
        this.parent(new Element('div'), options);
        this.popup = new Element('div', {'class': 'ecs-Popup'});
        if(options.width){
            this.element.setStyle('width', options.width + 'px');
        }
        if(options.height){
            this.element.setStyle('height', options.height + 'px');
        }
        this.headElement = new Element('div', {'class': 'head'});
        this.popup.grab(this.headElement);
        this.popup.grab(this.element);

        var closeButton = new Element('a', {'class': 'close', html: 'close'});
        closeButton.addEvent('click', (function(){
            this.close();
            return false;
        }).bind(this));
        this.headElement.grab(closeButton);
        this.titleElement = new Element('span', {'class': 'title', html: options.title || ''});
        this.headElement.grab(this.titleElement);
        this.hide();
        document.body.appendChild(this.popup);
        this.show();
        new Drag.Move(this.popup, {handle: this.headElement});
    },
    setTitle: function(title){
        this.titleElement.innerHTML = title;
    },
    show: function(){
        ecs.widgets.showModalOverlay();
        this.popup.setStyle('display', 'block');
    },
    hide: function(){
        this.popup.setStyle('display', 'none');
        ecs.widgets.hideModalOverlay();
    },
    close: function(){
        this.dispose();
    },
    dispose: function(){
        this.hide();
        this.parent();
        this.popup.dispose();
        this.fireEvent('dispose');
    }
});

window.addEvent('domready', function(){
    $$('a.open-in-popup').each(function(link){
        link.addEvent('click', function(){
            try{
                new ecs.widgets.Popup({url: link.href, width: 300, height: 200});
            }
            catch(e){
                console.log(e);
            }
            return false;
        });
    });
});
