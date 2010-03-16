(function($){
    var ecs = window.ecs = {};
    ecs.setupFormFieldHelpers = function(context){
        context = $(context || 'form');
        $('li.DateField > input', context).datepicker({dateFormat: 'dd.mm.yy'});
        $('li', context).each(function(){
            var maxlength = $('input[type=text]', this).attr('maxlength');
            var notes = [];
            if($(this).hasClass('required')){
                notes.push('required');
            }        
            if(maxlength && maxlength >= 0){
                notes.push('max. ' + maxlength + ' Zeichen');
            }
            if(notes.length){
                $(this).append('<span class="notes">' + notes.join(', ') + '</span>')
            }

            var formControls = $('li input, li textarea, li select', context);
            formControls.focus(function(){
                $(this).parent('li').addClass('focus');
            });
            formControls.blur(function(){
                $(this).parent('li').removeClass('focus');
            });
        
        });
    };

    ecs.setupFormSetHelpers = function(prefix){
        $('#' + prefix + '_formset .form').formset({
            prefix: prefix,
            formCssClass: prefix + '_formset',
            added: function(row){
                ecs.setupFormFieldHelpers(row);
            }
        });
    };
    
    ecs.submitMainForm = function(name){
        $('form.main.tabbed').attr('action', window.location.hash);
        $('form.main').find('input[type=submit][name=' + name + ']').click();
    };
    
    ecs.setupAutoSave = function(){
        var form = $('form.main');
        if(form.length){
            setInterval(function(){
                var lastSave = form.data('lastSave') || {};
                var currentData = form.serialize();
                if(lastSave.data != currentData){
                    lastSave.timestamp = new Date();
                    lastSave.data = currentData;
                    $.ajax({
                        url: window.location.href,
                        type: 'POST',
                        data: form.serialize() + '&autosave=autosave',
                        success: function(response){
                            console.log(response);
                            form.data('lastSave', lastSave);
                        }
                    });
                    
                }
            }, 10 * 1000);
        }
    };

    $(function(){
        if(!$('.tab_headers > li.active').length && !window.location.hash){
            $(".tab_headers > li:first-child").addClass('active');
        }
        $(".tab_headers").tabify();
        ecs.setupFormFieldHelpers();
        ecs.setupAutoSave();
    
        $(".tab").each(function(){
            if($('.errors', $(this)).length){ 
                $('.tab_headers > li a[href=#' + this.id + '-tab]').parent('li').addClass('errors');
            }
        });
        
        $('form.tabbed').each(function(){
            $(this).submit(function(){
                $(this).attr('action', window.location.hash);
            });
        });

        if($('a.submit_main_form').length){
            $('form.main').find('input[type=submit][name=submit]').css('display', 'none');
        }
        $('a.submit_main_form').click(function(){
            ecs.submitMainForm('submit');
            return false;
        });
        
        $('.doclist a.delete_document').click(function(){
            $(this).parent('div').find('input').remove();
            ecs.submitMainForm('upload');
            return false;
        });
        
    
    }); 

})(jQuery);