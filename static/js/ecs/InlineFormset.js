ecs.InlineFormSet = new Class({
    Implements: [Options, Events],
    options: {
        formSelector: '.form',
        prefix: null,
        idPrefix: 'id_',
        addButton: true,
        addButtonClass: 'add_row',
        addButtonText: '',
        removeButton: true,
        removeButtonClass: 'delete_row',
        removeButtonText: '',
        removeButtonInject: 'bottom',
        templateClass: 'template',
        canDelete: false,
        offset: 0
    },
    initialize: function(containers, options){
        console.log(containers);
        this.containers = $$(containers);
        this.setOptions(options);
        this.forms = containers.getElements(this.options.formSelector).flatten();
        if(!this.forms.length){
            return;
        }
        if(this.forms[0].hasClass(this.options.templateClass)){
            this.template = this.forms.pop();
            this.template.dispose();
            this.forms.splice(0, 1);
        }
        else{
            this.template = this.forms[0].clone(true, true);
        }
        this.isTable = this.containers[0].tagName.toUpperCase() == 'TABLE';
        ecs.clearFormFields(this.template);
        this.containers.each(function(container){
            this.addContainer(container);
        }, this);
        this.totalForms = $(this.options.idPrefix + this.options.prefix + '-TOTAL_FORMS');
        this.forms.each(function(form, index){
            this.setupForm(form, index, false);
        }, this);
    },
    createAddButton: function(container){
        return new Element('a', {
            html: this.options.addButtonText,
            'class': this.options.addButtonClass,
            events: {
                click: this.add.bind(this, container)
            }
        });
    },
    addContainer: function(container){
        if(this.options.addButton){
            var addButton = this.createAddButton(container);
            if(this.isTable){
                addButton.inject(container, 'after');
            }
            else{
                container.grab(addButton);
            }
        }
        this.containers.push(container);
    },
    removeContainer: function(container){
        for(var i=this.forms.length - 1;i>=0;i--){
            if(container.hasChild(this.forms[i])){
                this.remove(i);
            }
        }
        this.containers.erase(container);
    },
    getFormCount: function(){
        return this.forms.length;
    },
    setupForm: function(form, index, added){
        if(this.options.removeButton){
            var removeLink = new Element('a', {
                html: this.options.removeButtonText,
                'class': this.options.removeButtonClass,
                events: {
                    click: this.onRemoveButtonClick.bind(this)
                }
            });
            if(this.isTable){
                form.getElement('td').grab(removeLink);
            }
            else{
                removeLink.inject(form, this.options.removeButtonInject);
            }
        }
        if(added){
            var idField = form.getElement('input[name$=-id]');
            if(idField){
                idField.value = "";
            }
            ecs.setupFormFieldHelpers(form);
        }
        this.fireEvent('formSetup', [arguments, this].flatten());
    },
    updateIndex: function(form, index, oldIndex){
        var _update = (function(el, attr){
            var value = el.getProperty(attr);
            if(value){
                el.setProperty(attr, value.replace(/-.+?-/, '-' + (this.options.offset + index) + '-'));
            }
        }).bind(this);
        form.getElements('input,select,textarea').each(function(field){
            _update(field, 'name');
            _update(field, 'id');
        }, this);
        form.getElements('label').each(function(label){
            _update(label, 'for');
        });
        if(oldIndex !== null){
            this.fireEvent('formIndexChanged', [form, index, oldIndex]);
        }
    },
    onRemoveButtonClick: function(e){
        var form = e.target.getParent(this.options.formSelector);
        this.remove(this.forms.indexOf(form));
    },
    remove: function(index){
        var f = this.forms[index];
        if(this.options.canDelete){
            var name = this.options.prefix + '-' + (this.options.offset + index);
            var idField = $(this.options.idPrefix + name + '-id');
            if(idField && idField.value){
                var delName = name + '-DELETE';
                var checkbox = new Element('input', {
                    type: 'checkbox', 
                    style: 'display:none', 
                    name: delName, 
                    id: this.options.idPrefix + delName, 
                    checked: 'checked'
                });
                if(this.isTable){
                    f.getFirst('td').grab(checkbox);
                }
                else{
                    f.grab(checkbox);
                }
                f.setStyle('display', 'none');
                return;
            }
        }
        f.dispose();
        for(var i=index+1;i<this.forms.length;i++){
            this.updateIndex(this.forms[i], i - 1, i);
            this.forms[i - 1] = this.forms[i];
        }
        this.forms.pop();
        this.updateTotalForms(-1);
        this.fireEvent('formRemoved', [f, index]);
    },
    clear: function(){
        for(var i=this.forms.length - 1;i>=0;i--){
            this.remove(i);
        }
    },
    updateTotalForms: function(delta){
        this.totalForms.value = parseInt(this.totalForms.value) + delta;
    },
    add: function(container){
        var newForm = this.template.clone(true, true);
        var index = this.forms.length;
        this.updateIndex(newForm, index, null);
        this.setupForm(newForm, index, true);
        this.forms.push(newForm);
        this.updateTotalForms(+1);
        if(this.isTable){
            newForm.inject(container.getElement('tbody'));
        }
        else{
            newForm.inject(container.getElements(this.options.formSelector).getLast(), 'after');
        }

        newForm.getElements('textarea.flext').each(function(el) {
            new Flext(el);
        });

        newForm.getElements('textarea.maxlength').each(function(el) {
            el.addEvent('keypress', maxlength);
        });

        this.fireEvent('formAdded', [newForm, index])
    },
    getIndexForElement: function(el){
        for(var i=0;i<this.forms.length;i++){
            if(this.forms[i].hasChild(el)){
                return i;
            }
        }
        return -1;
    }
});
