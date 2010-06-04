ecs.TabbedForm = new Class({
    Implements: Options,
    options: {
        tabController: null,
        autosaveInterval: 15
    },
    initialize: function(form, options){
        this.form = $(form);
        this.options = options;
        var tabController = this.tabs = options.tabController;
        tabController.getTabs().each(function(tab){
            if(tab.panel.getElement('.errors')){
                tab.setClass('errors', true);
            }
        });
        tabController.addEvent('tabAdded', function(tab){
            if(tab.panel.getElement('.errors')){
                tab.setClass('errors', true);
            }
        });
        tabController.addEvent('tabSelectionChange', (function(tab){
            this.form.action = '#' + tab.panel.id;
        }).bind(this));
        if(this.options.autosaveInterval){
            this.lastSave = {
                data: this.form.toQueryString(),
                timestamp: new Date()
            };
            setInterval(this.autosave.bind(this), this.options.autosaveInterval * 1000);
            $(window).addEvent('unload', this.autosave.bind(this));
        }
    },
    autosave: function(force){
        var currentData = this.form.toQueryString();
        console.log('start autosave ..', arguments);
        if(force === true || (this.lastSave.data != currentData)){
            this.lastSave.timestamp = new Date();
            this.lastSave.data = currentData;
            var request = new Request({
                url: window.location.href,
                method: 'post',
                data: currentData + '&autosave=autosave',
                onSuccess: function(responseText, response){
                    ecs.messages.alert('Autosave', 'Das Formular wurde gespeichert.');
                }
            });
            request.send();
        }
    },
    submit: function(name){
        if(!name){
            return this.form.submit();
        }
        this.form.getElement('input[type=submit][name=' + name + ']').click();
    }
});
