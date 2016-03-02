ecs.TabbedForm = function(form, tabController, autosaveInterval) {
    this.form = $(form);
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
        $(window).unload(this.autosave.bind(this));
    }
};
ecs.TabbedForm.prototype = {
    _save: function(extraParameter) {
        var currentData = this.form.serialize();
        this.lastSaveData = currentData;

        $.post({
            url: window.location.href,
            data: currentData + '&' + extraParameter + '=' + extraParameter,
            success: function() {
                var now = new Date();
                $('#header .last_save').text(
                    'Last save: ' +
                    ('0' + now.getHours()).slice(-2) + ':' +
                    ('0' + now.getMinutes()).slice(-2)
                );
            },
        });
    },
    save: function() {
        this._save('save');
    },
    autosave: function() {
        if (this.autosaveDisabled ||
            this.lastSaveData == this.form.serialize())
            return;

        this._save('autosave');
    },
    submit: function(name) {
        this.autosaveDisabled = true;
        if (!name)
            return this.form.submit();
        this.form.find('input[type=submit][name=' + name + ']').click();
    }
};
