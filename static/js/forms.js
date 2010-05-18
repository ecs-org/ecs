(function(){
    if(!window.console){
        window.console = {log: $empty};
    }
    var ecs = $extend(window.ecs, {
        datepickerInputSelector: '.DateField > input, .DateTimeField > input[name$=_0]',
        Element: {
            setClass: function(cls, set){
                this[set ? 'addClass' : 'removeClass'](cls);
            }
        }
    });
    Element.implement(ecs.Element);
    
    MooEditable.Actions.bold.title = 'Fett';
    MooEditable.Actions.italic.title = 'Kursiv';
    MooEditable.Actions.underline.title = 'Unterstrichen';
    MooEditable.Actions.strikethrough.title = 'Durchgestrichen';
    MooEditable.Actions.indent.title = 'Einrücken';
    MooEditable.Actions.outdent.title = 'Ausrücken';
    MooEditable.Actions.undo.title = 'Rückgängig';
    MooEditable.Actions.redo.title = 'Wiederherstellen';

    ecs.Tab = new Class({
        Implements: Events,
        initialize: function(controller, header, panel, index){
            this.controller = controller;
            this.header = header;
            this.panel = panel;
            this.index = index;
            this.panel.setStyle('display', 'none');
            this.clickHandler = controller.onTabHeaderClick.bindWithEvent(controller, this);
            this.header.addEvent('click', this.clickHandler);
            this.selected = false;
        },
        setClass: function(cls, set){
            this.header.setClass(cls, set);
            this.panel.setClass(cls, set);
        },
        setSelected: function(selected){
            this.setClass(this.controller.options.selectedTabClass, selected);
            this.panel.setStyle('display', selected ? 'block' : 'none');
            this.selected = selected;
            this.fireEvent('select');
        },
        remove: function(){
            this.header.removeEvent('click', this.clickHandler);
            this.clickHandler = null;
            this.header.dispose();
            this.panel.dispose();
            this.fireEvent('remove');
        },
        getIndex: function(){
            return this.controller.tabs.indexOf(this);
        }
    });
    
    ecs.TabController = new Class({
        Implements: [Options, Events],
        options: {
            tabIdPrefix: 'tab-',
            selectedTabClass: 'active'
        },
        initialize: function(headerContainer, options){
            this.setOptions(options);
            this.tabs = [];
            this.selectedTab = null;
            this.headerContainer = headerContainer;
            var index = 0;
            var initialSelection = null;
            headerContainer.getChildren('li').each(function(header){
                var hash = header.getElement('a').href.split('#')[1];
                var panel = $(hash);
                var tab = new ecs.Tab(this, header, panel, index++);
                if(window.location.hash == '#' + hash){
                    initialSelection = tab;
                }
                this.tabs.push(tab);
            }, this);
            this.selectTab(initialSelection || this.tabs[0], true);
        },
        onTabHeaderClick: function(event, tab){
            this.selectTab(tab);
        },
        selectTab: function(tab, initial){
            if(tab == this.selectedTab){
                return;
            }
            if(this.selectedTab){
                this.selectedTab.setSelected(false);
            }
            this.selectedTab = tab;
            if(tab){
                tab.setSelected(true);
            }
            this.fireEvent('tabSelectionChange', tab, !!initial);
        },
        getSelectedTab: function(){
            return this.selectedTab;
        },
        getTabs: function(){
            return this.tabs;
        },
        getPanels: function(){
            return this.tabs.map(function(tab){ return tab.panel;})
        },
        getTabForElement: function(el){
            for(var i=0;i<this.tabs.length;i++){
                var tab = this.tabs[i];
                if(tab.panel == el || tab.panel.hasChild(el)){
                    return tab;
                }
            }
            return null;
        },
        getTab: function(index){
            return this.tabs[index];
        },
        addTab: function(header, panel, inject){
            panel.id = panel.id || this.options.tabIdPrefix + this.tabs.length;
            header = new Element('li', {html: '<a href="#' + panel.id + '">' + header + '</a>'});
            this.headerContainer.grab(header);
            if(inject){
                panel.inject(this.tabs.getLast().panel, 'after');
            }
            var tab = new ecs.Tab(this, header, panel, this.tabs.length);
            this.tabs.push(tab);
            this.fireEvent('tabAdded', tab);
            return tab;
        },
        removeTab: function(tab){
            this.tabs.erase(tab);
            tab.remove();
            if(tab == this.selectedTab){
                this.selectTab(this.tabs[tab.index - 1]);
            }
            this.fireEvent('tabRemoved', tab);
        }
    });

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
    
    ecs.InlineFormSet = new Class({
        Implements: [Options, Events],
        options: {
            formSelector: '.form',
            prefix: null,
            idPrefix: 'id_',
            addButton: true,
            addButtonClass: 'add_row',
            addButtonText: 'add',
            removeButton: true,
            removeButtonClass: 'delete_row',
            removeButtonText: 'remove',
            removeButtonInject: 'bottom',
            templateClass: 'template',
            canDelete: false,
            offset: 0
        },
        initialize: function(containers, options){
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
    
    ecs.InvestigatorFormSet = new Class({
        Extends: ecs.InlineFormSet,
    });
    
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
                field.grab(new Element('span', {
                    'class': 'notes',
                    'html': notes.join(', ')
                }));
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
    
    window.addEvent('domready', function(){
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
        
    }); 

})();
