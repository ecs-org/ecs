ecs.setupRichTextEditor = function(textArea, readonly){
    var display = new Element('div', {'class': 'rte_display', html: textArea.value});
    textArea.hide();
    display.inject(textArea, 'after');
    if(readonly){
        return
    }
    display.addEvent('click', function(e){
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
    context = $(context || document);
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
                star.inject(field);
            }
            //notes.push('required');
        }
        if(input){
            var maxlength = input.getProperty('maxlength');
            if(maxlength && maxlength > 0){
                notes.push('max. ' +  maxlength + ' Zeichen');
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
        var investigatorFormset = new ecs.InlineFormSet(ifs, {
            prefix: 'investigator',
            formSelector: '.investigator_tab',
            removeButtonInject: 'top',
            addButton: false,
            removeButton: !readonly,
            addButtonText: 'Weiteres Zentrum Hinzufügen',
            removeButtonText: 'Dieses Zentrum Entfernen',
            onFormSetup: function(form, index, added, formset){
                tabController.addTab('Zentrum ' + (index + 1) +  '', form);
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
    var tabHeaders = $$('.tab_headers')[0];
    if(tabHeaders){
        var tabController = new ecs.TabController(tabHeaders);
        var mainForm = document.getElement('form.tabbed.main');
        if(mainForm){
            var form = ecs.mainForm = new ecs.TabbedForm(mainForm, {
                tabController: tabController,
                autosaveInterval: 120
            });
        }
        var readonly = true;
        if(document.getElement('.form.main').tagName == 'FORM'){
            readonly = false;
        }
        ecs.setupInvestigatorFormSet(tabController, readonly);
    }
    ecs.setupFormFieldHelpers();

    var uploadButton = $('document_upload_button');
    if(uploadButton){
        uploadButton.addEvent('click', function(){
            form.autosaveDisabled = true;
        });
    }

    /* FIXME: cleanup the following code */
    $$('form.main').getElements('input[type=submit].hidden').each(function(button){
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
            form.submit('upload');
            return false;
        });
    });
};
