ecs.TabbedForm = function(form, tabController, autosaveInterval) {
    this.form = $(form);
    this.autosaveDisabled = false;
    this.autosave_xhr = null;

    tabController.tabs.forEach(function(tab) {
        if (tab.panel.find('.errors').length) {
            tab.setErrorState();
            tab.group.header.addClass('bg-danger'); // css('border','1px solid red');
        }
    });

    this.lastSaveData = this.form.serialize();
    if (autosaveInterval) {
        setInterval(this.autosave.bind(this), autosaveInterval * 1000);
        $(window).on('unload', this.autosave.bind(this));
    }
};
ecs.TabbedForm.prototype = {
    _save: function(extraParameter) {
        var currentData = this.form.serialize();
        this.lastSaveData = currentData;

        this.autosave_xhr = $.post({
            url: window.location.href,
            data: currentData + '&' + extraParameter + '=' + extraParameter,
            success: function() {
                var now = new Date();
                $('.last_save').text(
                    'Last save: ' +
                    ('0' + now.getHours()).slice(-2) + ':' +
                    ('0' + now.getMinutes()).slice(-2)
                );
            },
            complete: (function() {
                this.autosave_xhr = null;
            }).bind(this)
        });
    },
    save: function() {
        this._save('save');
    },
    autosave: function() {
        if (this.autosaveDisabled || this.autosave_xhr ||
            this.lastSaveData == this.form.serialize())
            return;

        this._save('autosave');
    },
    toggleAutosave: function(state) {
        this.autosaveDisabled = !state;
        if (!state && this.autosave_xhr)
            this.autosave_xhr.abort();
    },
    submit: function(name) {
        this.toggleAutosave(false);
        if (!name)
            return this.form.submit();
        this.form.find('input[type=submit][name=' + name + ']').click();
    }
};
