ecs.setupFormFieldHelpers = function(context){
    context = jQuery(context || document.body);

    jQuery(context)
        .find('.DateField > input, .DateTimeField > input[name$=_0]')
        .datepicker({
            format: 'dd.mm.yyyy',
            autoclose: true,
            weekStart: 1
        });

    jQuery(context).find('select[data-ajax--url]').select2();

    context.get(0).getElements('.CharField > textarea').each(function(textarea){    /* XXX */
        new ecs.textarea.TextArea(textarea);
    });
    context.get(0).getElements('li,th.label').each(function(field){                 /* XXX */
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
};

ecs.InvestigatorFormset = function(container, readonly) {
    this.container = container
    this.readonly = readonly;

    this.inline_formset = new ecs.InlineFormSet(this.container, {
        prefix: 'investigator',
        formSelector: '.investigator',
        addButton: false,
        removeButton: false,
        onFormAdded: (function(form, index) {
            form.find('.investigatoremployee_formset tbody').html('');
            this.employee_formset.addContainer(form.find('.investigatoremployee_formset'));
        }).bind(this),
        onFormRemoved: (function(form, index) {
            this.employee_formset.removeContainer(form.find('.investigatoremployee_formset'));
            this.generateJumpList();

            var form_count = this.inline_formset.forms.length;
            this.show(form_count-1 <= index ? form_count - 1 : index);
        }).bind(this),
        onFormIndexChanged: function(form, index) {
            form.find('input[name$=-investigator_index]').val(index);
        }
    });

    if (this.inline_formset.forms.length > 0) {
        this.generateJumpList();
        this.show(0);
    }

    if (this.readonly)
        return;

    /*** read/write ***/

    this.employee_formset = new ecs.InlineFormSet('.investigatoremployee_formset', {
        prefix: 'investigatoremployee',
        onFormAdded: (function(form, index) {
            var index = this.inline_formset.forms.findIndex(function(el) {
                return el.has(form).length;
            });
            form.find('input[name$=-investigator_index]').val(index);
        }).bind(this)
    });
};
ecs.InvestigatorFormset.prototype = {
    show: function(index) {
        jQuery('.investigator_list li').each(function(i) {
            jQuery(this).toggleClass('active', i == index);
        });

        this.inline_formset.forms.each(function(f, i){
            f.toggle(i == index);
        });
    },
    add: function() {
        this.inline_formset.add(this.container);
        var index = this.inline_formset.forms.length - 1;
        this.inline_formset.forms[index].find('.errors').removeClass('errors');
        this.generateJumpList();
        this.show(index);
    },
    generateJumpList: function() {
        var ul = jQuery('.investigator_list');
        ul.html('');

        this.inline_formset.forms.each(function(form, i){
            var li = jQuery('<li>');
            li.toggleClass('readonly', this.readonly);
            li.toggleClass('errors', !!form.find('.errors').length);

            var a = jQuery('<a>', {
                html: 'Zentrum ' + (i + 1),
                click: (function(ev){
                    ev.preventDefault();
                    this.show(i);
                }).bind(this)
            });
            li.append(a);

            if (!this.readonly && this.inline_formset.forms.length > 1) {
                var removeLink = jQuery('<a>', {
                    'class': 'fa fa-times-circle remove',
                    click: (function(ev) {
                        ev.preventDefault();
                        this.inline_formset.remove(i)
                    }).bind(this)
                });
                li.append(removeLink);
            }

            ul.append(li);
        }, this);

        if (!this.readonly) {
            var li = jQuery('<li>');
            var a = jQuery('<a>', {
                'class': 'fa fa-plus-circle',
                click: (function(ev) {
                    ev.preventDefault();
                    this.add();
                }).bind(this)
            });
            li.append(a);
            ul.append(li);
        }
    }
};

ecs.setupDocumentUploadForms = function(){
    var form = jQuery('.document_upload form');
    var upload_button = form.find('input[type="submit"]');
    var progress = form.find('progress');
    var warning = form.find('.warning');

    ecs.setupFormFieldHelpers(form);

    upload_button.click(function(ev) {
        ev.preventDefault();

        if(ecs.mainForm)
            ecs.mainForm.autosaveDisabled = true;
        warning.show();

        upload_button.hide();
        progress.show();

        xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', function(ev){
            if (ev.lengthComputable) {
                progress.attr('value', ev.loaded);
                progress.attr('max', ev.total);
                progress.html('' + Math.round(ev.loaded * 100 / ev.total) + '%');
            } else {
                progress.attr('value', null);
                progress.attr('max', null);
            }
        }, false);
        xhr.addEventListener('load', function(ev){
            jQuery('.upload_container').html(xhr.responseText);
        }, false);
        xhr.addEventListener('error', function(ev){
            progress.hide();
            upload_button.addClass('error').show();
        }, false);
        xhr.addEventListener('abort', function(ev){
            progress.hide();
            upload_button.addClass('error').show();
        }, false);
        xhr.open('POST', form.attr('action'));
        xhr.send(new FormData(form[0]));

        if(ecs.mainForm)
            ecs.mainForm.autosaveDisabled = false;
    });

    var file_field = jQuery('#id_document-file');
    var name_field = jQuery('#id_document-name');
    file_field.change(function() {
        var name = file_field.val().split('\\').slice(0)[0];

        var dot_offset = name.lastIndexOf('.');
        if (dot_offset >= 0)
            name = name.substring(0, dot_offset);

        if (!name_field.attr('disabled'))
            name_field.val(name);
    });

    jQuery('.doclist a.replace_document').click(function(ev) {
        ev.preventDefault();
        var link = jQuery(this);

        form.find('input[name="document-replaces_document"]')
            .val(jQuery(this).data('documentId'));

        jQuery('#replaced_document_name')
            .html(link.siblings('.document_display_name').html())
            .parent('li').show();

        form.find('select[name="document-doctype"]')
            .val(link.data('documentType'))
            .attr('disabled', true);
    });

    jQuery('#tabs-11 a.new_document').click(function(ev) {
        ev.preventDefault();

        form.find('input[name="document-replaces_document"]')
            .val(null);

        jQuery('#replaced_document_name')
            .html(null)
            .parent('li').hide();

        form.find('select[name="document-doctype"]')
            .val(null)
            .attr('disabled', false);
    });

    jQuery('.doclist a.delete_document').click(function(ev) {
        ev.preventDefault();
        jQuery('.upload_container').load(jQuery(this).attr('href'));
    });
};

ecs.setupForms = function(){
    var tabHeaders = $$('.tab_headers');
    var setup = {};
    if (tabHeaders.length) {
        var tabController = new ecs.TabController('.tab_header_groups a');
        var mainForm = jQuery('.form_main');
        var readonly = !mainForm.is('form');

        if (mainForm.length) {
            var form = ecs.mainForm = new ecs.TabbedForm(mainForm,
                tabController, readonly ? null : 120);
            setup.mainForm = form;
        }

        var ifs = jQuery('#tabs-12');
        if (ifs.length)
            new ecs.InvestigatorFormset(ifs, readonly);

        setup.tabController = tabController;
    }
    
    ecs.setupFormFieldHelpers();

    return setup;
};

ecs.setupWidgets = function(){
    jQuery('div[data-widget-url]').each(function() {
        var widget = jQuery(this);
        var options = {
            url: widget.data('widgetUrl'),
            reload_interval: parseInt(widget.data('widgetReloadInterval')) * 1000 || null,
        };
        new ecs.Widget(this, options);
    });
};

ecs.FormFieldController = function(options) {
    this.fields = jQuery(options.fields);

    if (options.disable)
        this.setDisabled(true);

    this.auto = options.auto || function() {
        this.fields.prop('checked', this.sources.is(':checked'));
        this.fields.change();
    };

    this.sources = jQuery(options.sources);
    this.sources.change((function(ev) {
        this.auto.apply(this);
    }).bind(this));
    if (options.sourceFieldClass)
        this.sources.addClass(options.sourceFieldClass);

    this.toggleTab = options.toggleTab;
    if (this.toggleTab) {
        this.fields.change(this.onFieldValueChange.bind(this));
        this.onFieldValueChange(null);
    }

    this.auto.apply(this);
};
ecs.FormFieldController.prototype = {
    requireField: function(f, enable) {
        var li = f.parents('li');
        li.toggleClass('required', enable);
        if (!enable)
            li.find('label .errorlist').hide();
    },
    onFieldValueChange: function(ev) {
        var enable = this.getValues().some(function(x) { return !!x;});
        this.toggleTab.tab.setDisabled(!enable);
        if (this.toggleTab.requiredFields)
            this.requireField(jQuery(this.toggleTab.requiredFields), enable);
    },
    setDisabled: function(disable) {
        this.fields.prop('disabled', disable);
    },
    getValues: function() {
        return this.fields.map((function(i, el) {
            return this.getValue(el);
        }).bind(this)).get();
    },
    getValue: function(field) {
        field = jQuery(field);
        if (field.attr('type') == 'checkbox')
            return field.is(':checked');
        return field.val();
    }
};

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
        if (!$defined(checked_input)) return;
        var value = checked_input.value;
        var receiver_prefix = id_prefix + 'receiver_';

        ['ec', 'involved', 'person'].each(function(x) {
            var el = container.getElement(receiver_prefix+x);
            if (x == value) {
                if (el) {
                    el.removeAttribute('disabled');
                }
                container.getElements(receiver_prefix+x+' + .errors').show();
            } else {
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
};

ecs.setupSubmitLinks = function(selector){
    jQuery(selector).click(function(ev) {
        ev.preventDefault();
        jQuery(this).parent('form').submit();
    });
};

ecs.stopPageLoad = function() {
    if (typeof(window.stop) !== 'undefined') {
        window.stop();
    } else {
        try { document.execCommand('Stop'); } catch(e){};
    }
};
