ecs.TabbedForm = new Class({
    Implements: Options,
    options: {
        tabController: null,
        autosaveInterval: 15
    },
    initialize: function(form, options){
        this.form = $(form);
        this.options = options;
        this.autosaveDisabled = false;
        var tabController = this.tabs = options.tabController;
        tabController.getTabs().each(function(tab){
            if(tab.panel.getElement('.errors')){
                tab.setClass('errors', true);
                tab.group.setHeaderClass('errors', true);
            }
        });
        tabController.addEvent('tabAdded', function(tab){
            if(tab.panel.getElement('.errors')){
                tab.setClass('errors', true);
                tab.group.setHeaderClass('errors', true);
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
    _save: function(callback, extraParameter){
        var currentData = this.form.toQueryString();

        this.lastSave.timestamp = new Date();
        this.lastSave.data = currentData;


        if(!callback){
            callback = function(){ecs.messages.alert('_save', 'Das Formular wurde gespeichert');};
        }
        if(!extraParameter){
            extraParameter = '_save';
        }

        var request = new Request({
            url: window.location.href,
            method: 'post',
            data: currentData + '&' + extraParameter + '=' + extraParameter,
            onSuccess: callback,
        });
        request.send();


    },
    save: function(){
        this._save(function(responseText, response){ecs.messages.alert('Save', 'Das Formular wurde gespeichert.');}, 'save');
    },
    autosave: function(force){
        if(!this.autosaveDisabled && (force === true || (this.lastSave.data != this.form.toQueryString()))){
            this._save(function(responseText, response){ecs.messages.alert('Autosave', 'Das Formular wurde gespeichert.');}, 'autosave');
        }
    },
    submit: function(name){
        this.autosaveDisabled = true;
        if(!name){
            return this.form.submit();
        }
        this.form.getElement('input[type=submit][name=' + name + ']').click();
    }
});
