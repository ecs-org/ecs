(function(){
    if(!window.console){
        window.console = {log: $empty};
    }
    var ecs = window.ecs = {
        messages: new Roar(),
        Element: {
            setClass: function(cls, set){
                this[set ? 'addClass' : 'removeClass'](cls);
            }
        }
    };
    Element.implement(ecs.Element);

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
                if(tab.panel.hasChild(el)){
                    return tab;
                }
            }
            return null;
        },
        getTab: function(index){
            return this.tabs[index];
        },
        addTab: function(header, panel){
            panel.id = panel.id || this.options.tabIdPrefix + this.tabs.length;
            header = new Element('li', {html: '<a href="#' + panel.id + '">' + header + '</a>'});
            this.headerContainer.grab(header);
            panel.inject(this.tabs.getLast().panel, 'after');
            var tab = new ecs.Tab(this, header, panel, this.tabs.length);
            this.tabs.push(tab);
            this.fireEvent('tabAdded', tab);
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
            autosave: 15
        },
        initialize: function(form, options){
            this.form = $(form);
            //this.setOptions(options);
            var tabController = options.tabController;
            tabController.getTabs().each(function(tab){
                if(tab.panel.getElement('.errors')){
                    tab.setClass('errors', true);
                }
            });
            tabController.addEvent('tabSelectionChange', (function(tab){
                this.form.action = '#' + tab.panel.id;
            }).bind(this));
            if(this.options.autosave){
                this.lastSave = {
                    data: this.form.toQueryString(),
                    timestamp: new Date()
                };
                setInterval(this.autosave.bind(this), this.options.autosave * 1000);
                $(window).addEvent('unload', this.autosave.bind(this));
            }
        },
        autosave: function(){
            console.log('start autosave ..');
            var currentData = this.form.toQueryString();
            if(this.lastSave.data != currentData){
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
        Implements: Options,
        options: {
            formSelector: '.form',
            prefix: null,
            idPrefix: 'id_',
            addButtonClass: 'add_row',
            removeButtonClass: 'delete_row',
            canDelete: false
        },
        initialize: function(container, options){
            this.container = $(container);
            this.setOptions(options);
            this.forms = container.getElements(this.options.formSelector);
            this.template = this.forms[0].clone(true, true);
            ecs.clearFormFields(this.template);
            this.totalForms = $(this.options.idPrefix + this.options.prefix + '-TOTAL_FORMS');
            this.container.grab(this.addButton = new Element('a', {
                html: 'add',
                'class': this.options.addButtonClass,
                events: {
                    click: this.add.bind(this)
                }
            }));
            this.forms.each(function(form, index){
                this.setupForm(form, index);
            }, this);
        },
        setupForm: function(form, index, added){
            form.grab(new Element('a', {
                html: 'remove',
                'class': this.options.removeButtonClass,
                events: {
                    click: (function(){
                        this.remove(index);
                    }).bind(this)
                }
            }));
            if(this.options.canDelete){
                var deleteLi = $(this.options.idPrefix + this.options.prefix + '-' + index + '-DELETE').getParent('li');
                deleteLi.setStyle('display', 'none');
            }
            if(added){
                ecs.setupFormFieldHelpers(form);
            }
        },
        updateIndex: function(form, index){
            function _update(el, attr){
                var value = el.getProperty(attr);
                if(value){
                    el.setProperty(attr, value.replace(/-\d+-/, '-' + index + '-'));
                }
            }
            form.getElements('input,select,textarea').each(function(field){
                _update(field, 'name');
                _update(field, 'id');
            }, this);
            form.getElements('label').each(function(label){
                _update(label, 'for');
            });
        },
        remove: function(index){
            var f = this.forms[index];
            if(this.options.canDelete){
                var idField = $(this.options.idPrefix + this.options.prefix + '-' + index + '-id');
                if(idField && idField.value){
                    $(this.options.idPrefix + this.options.prefix + '-' + index + '-DELETE').checked = true;
                    f.setStyle('display', 'none');
                    return;
                }
            }
            f.dispose();
            for(var i=index+1;i<this.forms.length;i++){
                this.updateIndex(this.forms[i], i - 1);
                this.forms[i - 1] = this.forms[i];
            }
            this.forms.pop();
            this.updateTotalForms(-1);
        },
        updateTotalForms: function(delta){
            this.totalForms.value = parseInt(this.totalForms.value) + delta;
        },
        add: function(){
            var newForm = this.template.clone(true, true);
            var index = this.forms.length;
            this.updateIndex(newForm, index);
            this.setupForm(newForm, index, true);
            this.forms.push(newForm);
            this.updateTotalForms(+1);
            newForm.inject(this.addButton, 'before');
        }
    });
    
    /*
    // TODO: implement #88
    ecs.InvestigatorFormSet = new Class({
        Extends: ecs.InlineFormSet,
        initialize: function(){
            
        }
    });
    
    ecs.InvestigatorEmployeeFormSet = new Class({
        Extends: ecs.InlineFormSet,
        initialize: function(container, options){
            this.parent(container, options);
            this.tab = this.options.tabController.getTabForElement(container);
        },
        setupForm: function(form, index, added){
            this.parent(form, index, added);
            form.getElement('input[type=hidden][name=$investigator_index]');
        }
    });
    */
    
    ecs.clearFormFields = function(context){
        context = $(context || document);
        context.getElements('input[type=text], textarea').each(function(input){
            input.setProperty('value', '');
        });
        context.getElements('.NullBooleanField > select', function(select){
            select.setProperty('value', 1);
        });
    };
    
    ecs.setupFormFieldHelpers = function(context){
        context = $(context || document);
        var datepicker = new DatePicker('.DateField > input', {
            format: 'd.m.Y',
            inputOutputFormat: 'd.m.Y',
            allowEmpty: true
        });
        context.getElements('li').each(function(field){
            var notes = [];
            var input = field.getFirst('input[type=text]');
            if(field.hasClass('required')){
                notes.push('required');
            }
            if(input){
                var maxlength = input.getProperty('maxlength');
                if(maxlength && maxlength > 0){
                    notes.push('max. ' +  maxlength + ' Zeichen');
                }
            }
            if(notes.length){
                field.grab(new Element('span', {
                    'class': 'notes',
                    'html': notes.join(', ')
                }));
            }
            field.getChildren('input,textarea,select').each(function(input){
                input.addEvent('focus', function(){
                    field.addClass('focus');
                });
                input.addEvent('blur', function(){
                    field.removeClass('focus');
                });
            });
        });
    };
    
    window.addEvent('domready', function(){
        var tabHeaders = $$('.tab_headers')[0];
        if(tabHeaders){
            var tabController = new ecs.TabController(tabHeaders);
            var mainForm = document.getElement('form.tabbed.main');
            if(mainForm){
                var form = new ecs.TabbedForm(mainForm, {
                    tabController: tabController,
                    autosave: 15
                });
            }
        }
        ecs.setupFormFieldHelpers();
        
        /* FIXME: cleanup the following code */
        $$('form.main').getElements('input[type=submit][name=submit]').each(function(button){
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
        
        /* FIXME: demo */
        function setupPartBLinks(context){
            context = $(context || document)
            context.getElements('.partb_remove').each(function(link){
                link.addEvent('click', function(){
                    var tab = tabController.getTabForElement(link);
                    tabController.removeTab(tab);
                    return false;
                });
            });
            context.getElements('.partb_add').each(function(link){
                link.addEvent('click', function(){
                    var panel = link.getParent('.tab').clone(true);
                    setupPartBLinks(panel);
                    tabController.addTab('Zentrum', panel);
                    return false;
                })
            });
        }
        setupPartBLinks();
    }); 

})();