ecs.setupRichTextEditor = function(textArea, readonly){
    var display = new Element('div', {'class': 'rte_display', html: textArea.value});
    textArea.hide();
    display.inject(textArea, 'after');
    if(readonly){
        return;
    }
    display.addEvent('click', function(e){
        if(textArea.disabled){
            return;
        }
        textArea.show();
        var editable = textArea.retrieve('MooEditable');
        if(editable){
            editable.attach();
        }
        else{
            editable = new MooEditable(textArea, {
                actions: 'bold italic underline strikethrough | indent outdent | undo redo',
                extraCSS: '*{font-size: 9pt;}'
            });
        }
        display.hide();
        editable.focus();
        e.stop();
    });
    document.body.addEvent('click', function(e){
        var editable = textArea.retrieve('MooEditable');
        if(editable && !editable.container.hasChild(e.target)){
            editable.detach();
            textArea.hide();
            display.innerHTML = textArea.value;
            display.show();
        }
    });
};

ecs.clearFormFields = function(context){
    context = $(context || document.body);
    context.getElements('input[type=text], textarea').each(function(input){
        input.setProperty('value', '');
    });
    context.getElements('.NullBooleanField > select', function(select){
        select.setProperty('value', 1);
    });
    context.getElements('span.errors').each(function(errors){
        errors.dispose();
    });
};

ecs.disabledFormFields = function(context, disable){
    context = $(context || document.body);
    context.getElements('input, select, textarea').each(function(field){
        if(!$defined(disable) || disable){
            field.setProperty('disabled', 'disabled');
        }
        else{
            field.removeProperty('disabled');
        }
    });
};

ecs.datepickerInputSelector = '.DateField > input, .DateTimeField > input[name$=_0]';

ecs.setupFormFieldHelpers = function(context){
    context = $(context || document.body);
    context.getElements(ecs.datepickerInputSelector).each(function(input){
        (new Element('span', {html: 'Kalender', 'class': 'datepicker_toggler'})).injectAfter(input);
    });
    var datepicker = new DatePicker(context.getElements(ecs.datepickerInputSelector), {
        format: 'd.m.Y',
        inputOutputFormat: 'd.m.Y',
        allowEmpty: true,
        toggleElements: context.getElements('.datepicker_toggler')
    });

    var setup_autocomplete = function(elm, values, max){
        var currentValues = values;
        elm.value = '';
        var tbl = null;
        var active = !!elm.getParent('form');
        if(active){
            tbl = new TextboxList(elm, {unique: true, max: max, plugins: {autocomplete: {onlyFromValues: true}}});
            tbl.container.addClass('textboxlist-loading');
        }
        new Request.JSON({url: elm.getProperty('x-autocomplete-url'), onSuccess: function(response){
            if(active){
                tbl.plugins['autocomplete'].setValues(response);
                tbl.container.removeClass('textboxlist-loading');
            }
            var labels = [];
            response.each(function(item){
                if(currentValues.contains(item[0])){
                    if(active){
                        tbl.add(item[1], item[0], item[2]);
                    }
                    else{
                        labels.push(item[1]);
                    }
                }
            });
            if(!active){
                (new Element('span', {html: labels.join(', ')})).replaces(elm);
            }
        }}).send();
    };

    context.getElements('.ModelMultipleChoiceField input.autocomplete').each(function(multiselect){
        setup_autocomplete(multiselect, multiselect.value.split(','), null);
    });
    context.getElements('.ModelChoiceField input.autocomplete').each(function(select){
        setup_autocomplete(select, [select.value], 1);
    });
    context.getElements('.CharField > textarea').each(function(textarea){
        new ecs.textarea.TextArea(textarea);
    });
    context.getElements('li,th.label').each(function(field){
        var notes = [];
        var input = null;
        if(field.tagName == 'TH'){
            var index = field.getParent('tr').getChildren('th').indexOf(field);
            var row = field.getParent('table').getElement('tbody > tr');
            if(row){
                input = row.getChildren('td')[index].getFirst('input[type=text]');
            }
        }
        else{
            input = field.getFirst('input[type=text]');
        }
        if(field.hasClass('required')){
            var span = field.getElement('span');
            var star = new Element('span', {html: '*', style: 'color:red', 'class': 'star'});
            if(span){
                star.inject(span, 'before');
            }
            else{
                star.inject(field.getElement('label'));
            }
            //notes.push('required');
        }
        if(input){
            var maxlength = input.getProperty('maxlength');
            if(maxlength && maxlength > 0){
                //notes.push('max. ' +  maxlength + ' Zeichen');
                var ml = 1 + parseInt(maxlength / 10)
                if(ml == 3){
                    ml = 4;
                }
                if(ml >= 5){
                    ml = 6;
                }
                field.addClass('max' + 10*ml);
            }
        }
        if(notes.length){
            (new Element('span', {
                'class': 'notes',
                'html': notes.join(', ')
            })).inject(input, 'after');
        }
    });
    /*
    context.getChildren('input[type=text],input[type=checkbox],textarea,select').each(function(input){
        input.addEvent('focus', function(){
            field.addClass('focus');
        });
        input.addEvent('blur', function(){
            field.removeClass('focus');
        });
    });
    */
};

ecs.InvestigatorFormset = new Class({
    Implements: [Options],
    options: {
        readonly: false,
        investigatorClass: 'investigator',
        addButtonClass: 'add_centre',
        investigatorEmployeeFormsetClass: 'investigatoremployee_formset',
        investigatorTranslation: 'Zentrum',
        jumpListClass: 'investigator_list',
        addButtonText: 'Weiteres Zentrum hinzufügen',
        investigatorHeaderClass: 'investigator_header'
    },
    initialize: function(container, options) {
        this.container = $(container);
        this.setOptions(options);

        this.inline_formset = new ecs.InlineFormSet(this.container, {
            prefix: 'investigator',
            formSelector: '.investigator',
            addButton: false,
            removeButton: false,
            removeButtonText: 'Dieses Zentrum Entfernen'
        });

        if (this.inline_formset.getFormCount() > 0) {
            this.generateJumpList();
            this.show(0);
        }

        if(this.options.readonly){
            return;
        }
        /*** read/write ***/

        this.employee_formset = new ecs.InlineFormSet($$('.'+this.options.investigatorEmployeeFormsetClass), {
            prefix: 'investigatoremployee',
            onFormAdded: (function(form, index, added){
                var indexField = form.getElement('input[name$=-investigator_index]');
                indexField.value = this.inline_formset.getIndexForElement(form);
            }).bind(this)
        });

        this.inline_formset.addEvent('formAdded', (function(form, index){
            form.getElement('.investigatoremployee_formset tbody').innerHTML = '';
            this.employee_formset.addContainer(form.getElement('.'+this.options.investigatorEmployeeFormsetClass));
        }).bind(this));

        this.inline_formset.addEvent('formRemoved', (function(form, index){
            this.employee_formset.removeContainer(form.getElement('.'+this.options.investigatorEmployeeFormsetClass));
            this.generateJumpList();

            var form_count = this.inline_formset.getFormCount();
            this.show(form_count-1 <= index ? form_count - 1 : index);
        }).bind(this));

        this.inline_formset.addEvent('formIndexChanged', (function(form, newIndex){
            form.getElement('.'+this.options.investigatorEmployeeFormsetClass).getElements('input[name$=-investigator_index]').each(function(indexField){
                indexField.value = newIndex;
            });
        }).bind(this));

    },
    show: function(index) {
        var i = 0;

        var ul = this.container.getElement('.'+this.options.jumpListClass);
        var offset = this.options.readonly ? 0 : 1;
        ul.getElements('li').each(function(li){
            if (i == index+offset) {
                li.addClass('active');
            } else {
                li.removeClass('active');
            }
            i += 1;
        }, this);

        i = 0;
        this.inline_formset.forms.each(function(f){
            (i == index) ? f.show() : f.hide();
            i += 1;
        });

        var header = this.container.getElement('.'+this.options.investigatorHeaderClass);
        header.innerHTML = '';

        var title = new Element('h3', {
            html: this.options.investigatorTranslation + ' ' + (index + 1),
        });
        title.inject(header);

        if (!this.options.readonly && this.inline_formset.getFormCount() > 1) {
            var removeLink =  new Element('a', {
                html: this.inline_formset.options.removeButtonText,
                'class': this.inline_formset.options.removeButtonClass,
                events: {
                    click: this.inline_formset.remove.bind(this.inline_formset, index)
                }
            });
            removeLink.inject(header);
        }
    },
    add: function() {
        this.inline_formset.add.apply(this.inline_formset, [this.container]);
        var new_form_index = this.inline_formset.getFormCount() - 1;
        this.inline_formset.forms[new_form_index].getElements('.errors').removeClass('errors');
        this.generateJumpList();
        this.show(new_form_index);
    },
    generateJumpList: function() {
        var ul = this.container.getElement('.'+this.options.jumpListClass);
        ul.innerHTML = '';

        if (!this.options.readonly) {
            var li = new Element('li');
            var a = new Element('a', {
                href: '',
                'class': this.options.addButtonClass+' add_row',
                html: this.options.addButtonText,
                events: {
                    click: (function(){
                        this.add();
                        return false;
                    }).bind(this)
                }
            });
            li.inject(ul);
            a.inject(li);
        }

        var i = 0;
        this.inline_formset.forms.each(function(){
            var li = new Element('li');
            if (this.options.readonly) {
                li.addClass('readonly');
            }
            if (this.inline_formset.forms[i].getElement('.errors')) {
                li.addClass('errors');
            }
            var a = new Element('a', {
                href: '',
                html: this.options.investigatorTranslation+' '+(i+1),
                events: {
                    click: (function(index){
                        this.show(index);
                        return false;
                    }).bind(this, i)
                }
            });

            li.inject(ul);
            a.inject(li);
        
            i += 1;
        }, this);
    }
});

ecs.setupForms = function(){
    var tabHeaders = $$('.tab_headers');
    var setup = {};
    if(tabHeaders.length){
        var tabController = new ecs.TabController($$('.tab_header_groups > li'));
        var mainForm = document.getElement('.form_main');
        var readonly = true;
        if(mainForm.tagName == 'FORM'){
            readonly = false;
        }
        if(mainForm){
            var form = ecs.mainForm = new ecs.TabbedForm(mainForm, {
                tabController: tabController,
                autosaveInterval: readonly ? 0 : 120
            });
            setup.mainForm = form;
        }

        var ifs = $('tabs-12');
        if (ifs) {
            var investigatorFormset = new ecs.InvestigatorFormset(ifs, {
                readonly: readonly
            });
        }

        setup.tabController = tabController;

        function updateHeaderHeight() {
            var tabHeight = setup.tabController.getSelectedTabGroup().container.getHeight();
            if(tabHeight){
                $$('.tab_header_groups')[0].setStyle('margin-bottom', tabHeight + 'px');
                $$('.tab_headers')[0].setStyle('margin-bottom', tabHeight + 'px');
            }
            $('content').setStyle('top', $('header').getHeight() + 'px');
        }
        setup.tabController.addEvent('tabGroupSelectionChange', updateHeaderHeight);
        window.addEvent('resize', updateHeaderHeight);
        $('header').setStyle('height', 'auto');
        updateHeaderHeight();
    }
    
    ecs.setupFormFieldHelpers();

    var uploadButton = $('document_upload_button');
    if(uploadButton){
        uploadButton.addEvent('click', function(){
            form.autosaveDisabled = true;
        });
    }

    /* XXX: cleanup the following code (FMD2) */
    $$('a.submit_main_form').each(function(link){
        link.addEvent('click', function(){
            form.submit('submit');
            return false;
        });
    });
    $$('.doclist a.delete_document').each(function(link){
        link.addEvent('click', function(){
            link.getParent('div').getElement('input').dispose();
            if(form){
                form.submit('upload');
            }
            else{
                link.getParent('form').submit();
            }
            return false;
        });
    });
    $$('.doclist a.replace_document').each(function(link){
        link.addEvent('click', function(){
            var container = link.getParent('div');
            var document_id = container.getElement('input').getAttribute('value');
            $('id_document-replaces_document').setAttribute('value', document_id);

            var replaced_document_name = $('replaced_document_name');
            replaced_document_name.innerHTML = container.getElement('span.document_display_name').innerHTML;
            replaced_document_name.getParent('li').show();

            var document_name = $('id_document-name');
            document_name.value = container.getElement('span.document_name').innerHTML;
            document_name.setAttribute('disabled', 'disabled');

            var document_type = $('id_document-doctype');
            document_type.value = container.getElement('span.document_type').innerHTML;
            document_type.setAttribute('disabled', 'disabled');

            return false;
        });
    });
    $$('#tabs-11 a.new_document').each(function(link){
        link.addEvent('click', function(){
            $('id_document-replaces_document').removeAttribute('value');
            var replaced_document_name = $('replaced_document_name');
            replaced_document_name.getParent('li').hide();

            var document_name = $('id_document-name');
            document_name.value = '';
            document_name.removeAttribute('disabled');

            var document_type = $('id_document-doctype');
            document_type.value = '';
            document_type.removeAttribute('disabled');

            return false;
        });
    });

    var document_replaces_document = $('id_document-replaces_document');
    if(document_replaces_document && document_replaces_document.value){
        var link = $$('.doclist input[value='+document_replaces_document.value+']')[0].getParent('div').getElement('a.replace_document');
        link.fireEvent('click');
    }
    
    return setup;
};

ecs.FormFieldController = new Class({
    initialize: function(fields, options){
        fields = fields.map($).erase(null);
        if(!fields.length || !fields[0].getParent('form')){
            return;
        }
        this.fields = fields;
        if(options.disable){
            this.setDisabled(true);
        }
        this.auto = options.auto || function(values){
            if(!values.length){
                return;
            }
            var autoValue = values.some(function(x){ return !!x;})
            for(var i=0;i<this.fields.length;i++){
                this.setValue(i, autoValue);
            }
        };
        this.sources = [];
        if(options.sources){
            options.sources.each(function(el){
                el = $(el);
                this.sources.push(el);
                el.addEvent('change', this.onChange.bind(this));
                if(options.sourceFieldClass){
                    el.addClass(options.sourceFieldClass);
                }
            }, this);
        }
        this.toggleTab = options.toggleTab;
        if(this.toggleTab){
            this.fields.each(function(f){
                f.addEvent('change', this.onFieldValueChange.bind(this));
            }, this);
            this.onFieldValueChange(null, true);
        }
        this.onChange(null, true);
    },
    requireField: function(f, enable){
        var li = f.getParent('li');
        var label = li.getChildren('label')[0];
        if(enable && !li.hasClass('required')){
            li.addClass('required');
            var star = new Element('span', {'class': 'star', 'style': 'color: red;'});
            star.innerHTML = '*';
            var paperform_number = label.getChildren('.paperform_number')[0];
            if(paperform_number){
                star.injectBefore(paperform_number);
            } else {
                star.inject(label, 'bottom');
            }
        } else if(!enable && li.hasClass('required')){
            li.removeClass('required');
            label.getChildren('.star').each(function(s){
                s.dispose();
            });
            li.getChildren('.errorlist').each(function(e){
                e.hide();
            });
        }
    },
    onFieldValueChange: function(e, initial){
        if(this.toggleTab){
            var enable = this.getValues().some(function(x){ return !!x;});
            this.toggleTab.tab.setDisabled(!enable);
            if(this.toggleTab.requiredFields){
                this.toggleTab.requiredFields.map($).each(function(f){
                    this.requireField(f, enable);
                }, this);
            }
        }
    },
    onChange: function(e, initial){
        var values = this.sources.map(this.getValue, this);
        this.auto.call(this, values, !!initial);
    },
    setDisabled: function(disable){
        this.fields.each(function(f){
            if(disable){
                f.setProperty("disabled", "disabled");
            }
            else{
                f.removeProperty("disabled");
            }
        });
    },
    getValues: function(){
        return this.fields.map(this.getValue, this);
    },
    getValue: function(field){
        if(field.type == 'checkbox'){
            return field.checked;
        }
        return field.value;
    },
    setValue: function(i, val){
        var f = this.fields[i];
        if(f.type == 'checkbox'){
            f.checked = !!val;
        }
        else{
            f.value = val;
        }
        f.fireEvent('change');
    },
    setValues: function(values){
        values.each(function(val, i){
            this.setValue(i, val);
        }, this);
    }
});

ecs.setupMessagePopup = function(container, prefix) {
    container = $(container);

    var name_prefix = '';
    var id_prefix = '#id_';
    if (prefix) {
        name_prefix = prefix + '-';
        id_prefix = '#id_' + prefix + '-';
    }

    function show_selected_receiver() {
        var checked_input = container.getElement('input[name="' + name_prefix + 'receiver_type"][checked]');
        var value = checked_input.value;
        var receiver_prefix = id_prefix + 'receiver_';

        ['ec', 'involved', 'person'].each(function(x){
            if (x == value) {
                var el = container.getElement(receiver_prefix+x);
                console.log(el);
                if (el) {
                    el.removeAttribute('disabled');
                }
                container.getElements(receiver_prefix+x+' + .errors').show();
            } else {
                var el = container.getElement(receiver_prefix+x);
                console.log(el);
                if (el) {
                    el.setAttribute('disabled', 'disabled');
                }
                container.getElements(receiver_prefix+x+' + .errors').hide();
            }
        });
    }

    show_selected_receiver();

    container.getElements('input[name="' + name_prefix + 'receiver_type"]').each(function(elm){
        elm.addEvent('change', function(){
            show_selected_receiver();
        });
    }, this);
}

/* windmill helper stuff*/
ecs.windmill_upload = function(filename) {
    var element = document.createElement('UploadAssistantDataElement');
    element.setAttribute('target_id', 'id_document-file');
    element.setAttribute('target_value', filename);
    document.documentElement.appendChild(element);

    var evt = document.createEvent('Events');
    evt.initEvent('UploadAssistantSetValue', true, false);
    element.dispatchEvent(evt);
}


