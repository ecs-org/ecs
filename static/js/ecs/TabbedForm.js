ecs.TabbedForm = new Class({
    initialize: function(form, tabController, autosaveInterval) {
        this.form = jQuery(form);
        this.autosaveDisabled = false;

        tabController.tabs.forEach(function(tab) {
            if (tab.panel.find('.errors').length) {
                tab.toggleClass('errors', true);
                tab.group.header.toggleClass('errors', true);
            }
        });

        this.lastSaveData = this.form.serialize();
        if (autosaveInterval) {
            setInterval(this.autosave.bind(this), autosaveInterval * 1000);
            jQuery(window).unload(this.autosave.bind(this));
        }
    },
    _save: function(callback, extraParameter) {
        var currentData = this.form.serialize();

        this.lastSaveData = currentData;

        if (!callback) {
            callback = function() {
                ecs.messages.alert('_save', 'Das Formular wurde gespeichert');
            };
        }

        if (!extraParameter)
            extraParameter = '_save';

        var request = new Request({
            url: window.location.href,
            method: 'post',
            data: currentData + '&' + extraParameter + '=' + extraParameter,
            onSuccess: callback,
        });
        request.send();
    },
    save: function() {
        this._save(function(responseText, response) {
            ecs.messages.alert('Speichern', 'Das Formular wurde gespeichert.');
        }, 'save');
    },
    autosave: function() {
        if (this.autosaveDisabled ||
            this.lastSaveData == this.form.serialize())
            return;

        this._save(function(responseText, response) {
            ecs.messages.alert('Autosave', 'Das Formular wurde gespeichert.');
        }, 'autosave');
    },
    submit: function(name) {
        this.autosaveDisabled = true;
        if (!name)
            return this.form.submit();
        this.form.find('input[type=submit][name=' + name + ']').click();
    }
});
