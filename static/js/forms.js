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

            var formControls = $('input,textarea,select', this);
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
    
    ecs.autosave = function(form){
        var lastSave = form.data('lastSave');
        var currentData = form.serialize();
        if(lastSave.data != currentData){
            lastSave.timestamp = new Date();
            lastSave.data = currentData;
            $.ajax({
                url: window.location.href,
                type: 'POST',
                data: form.serialize() + '&autosave=autosave',
                success: function(response){
                    //console.log(response);
                    form.data('lastSave', lastSave);
                }
            });
        }
    };
    
    ecs.setupAutoSave = function(){
        var form = $('form.main');
        if(form.length){
            $(form).data('lastSave', {
                timestamp: new Date(),
                data: form.serialize()
            });
            $(window).bind('unload', function(){
                ecs.autosave(form);
            });
            setInterval(function(){
                ecs.autosave(form);
            }, 120 * 1000);
        }
    };

    ecs.partbNo = 1;
    ecs.partbOffset = $('.tab_headers > li').size() - 1;

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
        

        //
        // handlers for adding and removing part B tabs
        //

        $('.partb_add').click(function() {
          ecs.partbNo++;
          // add tab link
          var tabNo = ecs.partbNo + ecs.partbOffset;
          var tabItem = $('<li><a href="#tabs-' + tabNo + '-tab">Zentrum</a></li>');
          $('.tab_headers').append(tabItem);
          // add fields
          var partb = $('div #tabs-' + (tabNo - 1)).clone();

          // TODO fixup copy
          partb.attr('id', 'tabs-' + tabNo);

          // copy
          partb.appendTo('div #tabs');
        });

        $('.partb_remove').click(function() {
          if (ecs.partbNo < 2) {
            alert('Mehr darf nicht! (Und diese Meldung sollte nie angezeigt werden)');
            return;
          }

          // TODO some warning, because entered data might get lost
          // TODO better disable than delete

          // TODO these ops remove the LAST not CURRENT tab, change this
          $('.tab_headers li:last').remove();
          var tabNo = ecs.partbNo + ecs.partbOffset;
          $('div #tabs-' + tabNo).remove();

          ecs.partbNo--;
        });
    
    }); 

})(jQuery);