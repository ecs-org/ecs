ecs.InlineFormSet = function(containers, options) {
    var containers = jQuery(containers);

    this.options = jQuery.extend({
        formSelector: '.form',
        prefix: null,
        addButton: true,
        addButtonText: '',
        removeButton: true,
        canDelete: false
    }, options);

    this.forms = containers.find(this.options.formSelector)
        .map(function() {
            return jQuery(this);
        }).get();
    if (!this.forms.length)
        return;

    if (this.forms[0].hasClass('template')) {
        this.template = this.forms.shift();
        this.template.remove();
    } else {
        this.template = this.forms[0].clone();
    }

    /* Clear form fields. */
    this.template.find('input[type=text], textarea').val('');
    this.template.find('.NullBooleanField > select').val(1);
    this.template.find('span.errors').remove();

    this.isTable = containers.is('table');
    containers.each((function(i, el) {
        this.addContainer(jQuery(el));
    }).bind(this))
    this.totalForms = jQuery('#id_' + this.options.prefix + '-TOTAL_FORMS');
    this.forms.forEach(function(form, i) {
        this.setupForm(form, i, false);
    }, this);
};
ecs.InlineFormSet.prototype = {
    createAddButton: function(container){
        return jQuery('<a>', {
            'class': 'add_row',
            text: this.options.addButtonText,
            click: (function(ev) {
                ev.preventDefault();
                this.add(container);
            }).bind(this)
        });
    },
    createRemoveButton: function(){
        return jQuery('<a>', {
            'class': 'delete_row',
            click: (function(ev) {
                ev.preventDefault();
                var form = jQuery(ev.target).parents(this.options.formSelector);
                var index = this.forms.findIndex(function(el) {
                    return el.is(form);
                });
                this.remove(index);
            }).bind(this)
        });
    },
    addContainer: function(container){
        if(this.options.addButton){
            var addButton = this.createAddButton(container);
            container[this.isTable ? 'after' : 'append'](addButton);
        }
    },
    removeContainer: function(container){
        for (var i = 0; i < this.forms.length; ) {
            if (container.has(this.forms[i]).length) {
                this.remove(i);
                continue;
            }
            i++;
        }
    },
    setupForm: function(form, index, added){
        if (this.options.removeButton) {
            var removeLink = this.createRemoveButton();
            if (this.isTable) {
                form.find('td:first').append(removeLink);
            } else {
                form.append(removeLink);
            }
        }
        if (added) {
            form.find('input[name$=-id]').val('');
            ecs.setupFormFieldHelpers(form);
        }
    },
    updateIndex: function(form, index){
        form.find('input, select, textarea, label')
            .not(form.find('.inline_formset input, .inline_formset select,' +
                '.inline_formset textarea, .inline_formset label'))
            .each(function() {
                var el = jQuery(this);

                for (var f of ['id', 'name', 'for']) {
                    var val = el.attr(f);
                    if (val)
                        el.attr(f, val.replace(/-.+?-/, '-' + index + '-'));
                }
            });

        if (this.options.onFormIndexChanged)
            this.options.onFormIndexChanged(form, index);
    },
    remove: function(index){
        var f = this.forms.splice(index, 1)[0];
        this.totalForms.val(this.forms.length);

        if(this.options.canDelete){
            var name = this.options.prefix + '-' + index;
            if(jQuery('#id_' + name + '-id').val()){
                var delName = name + '-DELETE';
                var checkbox = jQuery('<input>', {
                    type: 'checkbox', 
                    style: 'display:none', 
                    name: delName, 
                    id: 'id_' + delName,
                    checked: 'checked'
                });
                if (this.isTable) {
                    f.find('td').first().append(checkbox);
                } else {
                    f.append(checkbox);
                }
                f.hide();
                return;
            }
        }
        f.remove();

        for (var i = index; i < this.forms.length; i++)
            this.updateIndex(this.forms[i], i);

        if (this.options.onFormRemoved)
            this.options.onFormRemoved(f, index);
    },
    add: function(container){
        var newForm = this.template.clone(true, true);
        var index = this.forms.length;
        this.updateIndex(newForm, index);
        this.setupForm(newForm, index, true);

        this.forms.push(newForm);
        this.totalForms.val(this.forms.length);

        if(this.isTable){
            container.find('tbody').append(newForm);
        } else {
            container.find(this.options.formSelector).last().after(newForm);
        }

        if (this.options.onFormAdded)
            this.options.onFormAdded(newForm, index);
    }
};
