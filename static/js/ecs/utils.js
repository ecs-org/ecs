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
    context.getElements('.ModelMultipleChoiceField input.autocomplete').each(function(multiselect){
        var currentValues = multiselect.value.split(',');
        multiselect.value = '';
        var tbl = null;
        var active = !!multiselect.getParent('form');
        if(active){
            tbl = new TextboxList(multiselect, {unique: true, plugins: {autocomplete: {onlyFromValues: true}}});
            tbl.container.addClass('textboxlist-loading');
        }
        new Request.JSON({url: multiselect.getProperty('x-autocomplete-url'), onSuccess: function(response){
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
                (new Element('span', {html: labels.join(', ')})).replaces(multiselect);
            }
        }}).send();
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

ecs.setupInvestigatorFormSet = function(tabController, readonly){
    var ifs = $('investigator_formset');
    if(ifs){
        var centerTabGroup = tabController.getTabGroupForElement('submission_headers');
        var investigatorFormset = new ecs.InlineFormSet(ifs, {
            prefix: 'investigator',
            formSelector: '.investigator_tab',
            removeButtonInject: 'top',
            addButton: false,
            removeButton: !readonly,
            addButtonText: 'Weiteres Zentrum Hinzufügen',
            removeButtonText: 'Dieses Zentrum Entfernen',
            onFormSetup: function(form, index, added, formset){
                tabController.addTab(centerTabGroup, 'Zentrum ' + (index + 1) +  '', form);
                if(readonly){
                    return;
                }
                var addButton = formset.createAddButton(ifs);
                addButton.inject(form, 'top');
            },
            onFormRemoved: function(form, index){
                var tab = tabController.getTabForElement(form);
                tabController.removeTab(tab);
            }
        });
        if(readonly){
            return;
        }
        // HACK
        if(investigatorFormset.getFormCount() == 1){
            investigatorFormset.forms[0].getElement('.delete_row').hide();
        }
        else{
            investigatorFormset.forms.each(function(f){
                f.getElement('.delete_row').show();
            });
        }

        
        var employeeFormSet = new ecs.InlineFormSet($$('.investigatoremployee_formset'), {
            prefix: 'investigatoremployee',
            onFormAdded: function(form, index, added){
                var indexField = form.getElement('input[name$=-investigator_index]');
                indexField.value = investigatorFormset.getIndexForElement(form);
            }
        });
        investigatorFormset.addEvent('formAdded', function(form, index){
            form.getElement('.investigatoremployee_formset tbody').innerHTML = '';
            employeeFormSet.addContainer(form.getElement('.investigatoremployee_formset'));
            // HACK
            if(investigatorFormset.getFormCount() > 1){
                investigatorFormset.forms.each(function(f){
                    f.getElement('.delete_row').show();
                });
            }
        });
        investigatorFormset.addEvent('formRemoved', function(form, index){
            employeeFormSet.removeContainer(form.getElement('.investigatoremployee_formset'));
            // HACK
            if(investigatorFormset.getFormCount() == 1){
                investigatorFormset.forms[0].getElement('.delete_row').hide();
            }
        });
        investigatorFormset.addEvent('formIndexChanged', function(form, newIndex){
            form.getElement('.investigatoremployee_formset').getElements('input[name$=-investigator_index]').each(function(indexField){
                indexField.value = newIndex;
            });
        });
    }
};

ecs.setupForms = function(){
    var tabHeaders = $$('.tab_headers');
    var setup = {};
    if(tabHeaders.length){
        var tabController = new ecs.TabController($$('.tab_header_groups > li'));
        var mainForm = document.getElement('.innerwrap');
        if(mainForm){
            var form = ecs.mainForm = new ecs.TabbedForm(mainForm, {
                tabController: tabController,
                autosaveInterval: 120
            });
            setup.mainForm = form;
        }
        var readonly = true;
        if(document.getElement('.form_main').tagName == 'FORM'){
            readonly = false;
        }
        ecs.setupInvestigatorFormSet(tabController, readonly);
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
    $$('form_main').getElements('input[type=submit].hidden').each(function(button){
        button.setStyle('display', 'none');
    });
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
    
    return setup;
};

ecs.FormFieldController = new Class({
    initialize: function(fields, options){
        fields = fields.map($);
        if(!fields[0].getParent('form')){
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
    onFieldValueChange: function(e, initial){
        if(this.toggleTab){
            var enable = this.getValues().some(function(x){ return !!x;});
            this.toggleTab.tab.setDisabled(!enable);
            if(this.toggleTab.requiredFields){
                this.toggleTab.requiredFields.map($).each(function(f){
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


