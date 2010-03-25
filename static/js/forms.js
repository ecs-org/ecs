(function(){
    var ecs = window.ecs = {};
    ecs.Tab = new Class({
        Implements: Events,
        initialize: function(header, panel, index){
            this.header = header;
            this.panel = panel;
            this.index = index;
            this.panel.setStyle('display', 'none');
        },
        setClass: function(cls, set){
            if(set){
                this.header.addClass(cls);
                this.panel.addClass(cls);
            }
            else{
                this.header.removeClass(cls);
                this.panel.removeClass(cls);
            }
        },
        setSelected: function(selected){
            this.setClass('active', selected);
            this.panel.setStyle('display', selected ? 'block' : 'none');
            this.fireEvent('select');
        }
    });
    
    ecs.TabController = new Class({
        Implements: [Options, Events],
        options: {
            
        },
        initialize: function(headerContainer, options){
            this.setOptions(options);
            this.tabs = [];
            this.selectedTab = null;
            var index = 0;
            var initialSelection = null;
            headerContainer.getChildren('li').each(function(header){
                var hash = header.getElement('a').href.split('#')[1];
                var panel = $(hash);
                var tab = new ecs.Tab(header, panel, index++);
                this.tabs.push(tab);
                if(window.location.hash == '#' + hash){
                    initialSelection = tab;
                }
                header.addEvent('click', (function(){
                    this.selectTab(tab);
                }).bind(this));
            }, this);
            this.selectTab(initialSelection || this.tabs[0]);
        },
        selectTab: function(tab){
            if(tab == this.selectedTab){
                return;
            }
            if(this.selectedTab){
                this.selectedTab.setSelected(false);
            }
            this.selectedTab = tab;
            tab.setSelected(true);
            this.fireEvent('tabSelectionChange', tab);
        },
        getSelectedTab: function(){
            return this.selectedTab;
        },
        getTabs: function(){
            return this.tabs;
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
            this.setOptions(options);
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
                        console.log('auto-saved');
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
            removeButtonClass: 'remove_row'
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
            this.forms[index].dispose();
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
    
    ecs.clearFormFields = function(context){
        context = $(context || document);
        context.getElements('.IntegerField input[type=text], .CharField input[type=text], .CharField textarea').each(function(input){
            input.setProperty('value', '');
        });
        context.getElements('.NullBooleanField > select', function(select){
            select.setProperty(value, 1);
        });
    };
    
    ecs.setupFormFieldHelpers = function(context){
        context = $(context || document);
        var datepicker = new DatePicker('.DateField > input', {
            format: 'd.m.Y',
            inputOutputFormat: 'd.m.Y'
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
    
    ecs.partbNo = 1;
    //ecs.partbOffset = $('.tab_headers > li').size() - 1;

    window.addEvent('domready', function(){
        var tabController = new ecs.TabController($$('.tab_headers')[0]);
        var form = new ecs.TabbedForm(document.getElement('form.tabbed.main'), {
            tabController: tabController,
            autosave: 15
        });

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
    
    }); 

})();