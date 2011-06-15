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
    load: function(url, form, callback){
        var request = new Request.HTML({
            url: url || (form ? form.getProperty('action') : this.url),
            method: form ? form.method : 'get',
            update: this.element,
            data: form ? form.toQueryString() : ''
        });
        if(url){
            this.url = url;
        }
        request.addEvent('success', (function(){
            if(callback){
                var stop = callback();
                if($defined(stop) && !stop){
                    return;
                }
            }
            this.onSuccess();
        }).bind(this));
        request.send();
    },
    onSuccess: function(){
        var self = this;
        this.element.scrollTo(0, 0);
        ecs.widgets.enablePopupHandlers(this.element, this);
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
    onPopupSpawned: function(popup){
        this.fireEvent('popupSpawned', popup);
    },
    dispose: function(){
        this.element.eliminate('ecs.widgets.Widget');
    }
});

ecs.widgets.Popup = new Class({
    Extends: ecs.widgets.Widget,
    initialize: function(options){
        options = options || {};
        this.context = options.context || null;
        this.parent(new Element('div'), options);
        this.popup = new Element('div', {'class': 'ecs-Popup'});
        this.popup.store('ecs.widgets.Popup', this);
        if(options.width){
            this.popup.setStyle('width', options.width + 'px');
        }
        if(options.height){
            this.popup.setStyle('height', options.height + 'px');
        }
        this.keypress = this.keyHandler.bind(this);
        this.resize = this.resizeHandler.bind(this);
        this.headElement = new Element('div', {'class': 'head'});
        this.popup.grab(this.headElement);
        this.popup.grab(this.element);

        var closeButton = new Element('a', {'class': 'close', html: 'close'});
        closeButton.addEvent('click', (function(){
            this.close();
            return false;
        }).bind(this));
        this.headElement.grab(closeButton);
        this.titleElement = new Element('h4', {'class': 'title', html: options.title || ''});
        this.headElement.grab(this.titleElement);
        this.hide();
        document.body.appendChild(this.popup);
        if(this.url){
            ecs.widgets.showModalOverlay();
        } else {
            this.show();
        }
        $(window).addEvent('keyup', this.keypress);
        $(window).addEvent('resize', this.resize);
        new Drag.Move(this.popup, {handle: this.headElement});
    },
    setTitle: function(title){
        this.titleElement.innerHTML = title;
    },
    onSuccess: function(){
        this.parent();
        this.show();
        /* the popup content has changed, so we have to resize and recenter */
        this.resizeHandler();
    },
    resizeHandler: function(){
        var popupSize = null;
        var parent = this.popup.getParent();

        this.popup.setStyles({
            'width': null,
            'height': null
        });

        /* set size */
        popupSize = this.popup.getSize();
        this.popup.setStyles({
            'max-width': parent.getWidth() - 50,
            'max-height': parent.getHeight() - 50,
            'width': popupSize.x,
            'height': popupSize.y
        });

        /* center on screen */
        var windowSize = window.getSize();
        popupSize = this.popup.getSize();
        this.popup.setStyles({
            'left': ((windowSize.x - popupSize.x) / 2) + 'px',
            'top': ((windowSize.y - popupSize.y) / 2) + 'px',
        });
    },
    show: function(){
        ecs.widgets.showModalOverlay();
        this.popup.setStyle('display', 'block');
        this.resizeHandler();
    },
    hide: function(){
        this.popup.setStyle('display', 'none');
        ecs.widgets.hideModalOverlay();
        $(window).removeEvent('keyup', this.keypress);
        $(window).removeEvent('resize', this.resize);
    },
    close: function(){
        this.dispose();
    },
    keyHandler: function(evt){
        if(evt.key == 'esc'){
            this.dispose();
        }
    },
    dispose: function(){
        this.hide();
        this.parent();
        this.popup.dispose();
        this.fireEvent('dispose');
    }
});

ecs.widgets.enablePopupHandlers = function(context, widget){
    context.getElements('a.open-in-popup').each(function(link){
        if(link.getParent('.ecs-Popup')){
            link.addClass('open-in-widget');
            return;
        }
        link.addEvent('click', function(){
            try{
                var popup = new ecs.widgets.Popup({url: link.href, width: 700, height: 500});
                if(widget){
                    widget.onPopupSpawned(popup);
                }
            }
            catch(e){
                //console.log(e);
            }
            return false;
        });
    });
    context.getElements('a.close-popup').each(function(link){
        var parent = link.getParent('.ecs-Popup');
        if(!parent){
            return;
        }
        var popup = parent.retrieve('ecs.widgets.Popup');
        link.addEvent('click', function(){
            popup.load(link.href, null, function(){
                popup.dispose();
            });
            return false;
        });
    });
};

window.addEvent('domready', function(){
    ecs.widgets.enablePopupHandlers(document.body);
});
