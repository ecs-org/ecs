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

    ecs.info = function(str) {
        $('#info').html(str).css('opacity', '1.0');
        $('#info').slideDown(2 * 1000, function () {
          $('#info').fadeTo(4 * 1000, 0.4, function () {
            $('#info').slideUp(2 * 1000);
          })
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
                    ecs.info('auto-saved');
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
        // (using some code & ideas from jquery.formset.js)
        //

        ecs.updateElementIndex = function(elem, prefix, ndx) {
	    var idRegex = new RegExp('(' + prefix + '-\\d+-)|(^)');
            var replacement = prefix + '-' + ndx + '-';
            if (elem.attr('for')) elem.attr('for', elem.attr('for').replace(idRegex, replacement));
            if (elem.attr('id')) elem.attr('id', elem.attr('id').replace(idRegex, replacement));
            if (elem.attr('name')) elem.attr('name', elem.attr('name').replace(idRegex, replacement));
        };


        /* Part B add */
        $('.partb_add').click(function() {
          ecs.partbNo++;
          // add tab link
          var tabNo = ecs.partbNo + ecs.partbOffset;
          var tabItem = $('<li><a href="#tabs-' + tabNo + '-tab">Zentrum</a></li>');
          $('.tab_headers').append(tabItem);
          // add fields
          var partb = $('#tabs-' + (tabNo - 1)).clone(true);
          partb.appendTo('#tabs');

          // fixup copy:

          // fix tab id
          $('#tabs >div:last').attr('id', 'tabs-' + tabNo); 

          // remove management_form data copies
          $('#tabs-' + tabNo + ' #id_investigator-TOTAL_FORMS').remove();
          $('#tabs-' + tabNo + ' #id_investigator-INITIAL_FORMS').remove();
          
          // TODO drop all but first InvestigatorEmployee entries
          // TODO fixups due to we can use only one Investigator Employee formset
          
          // fix form id's
          $('#tabs-' + tabNo).find('input,select,textarea,label').each(function() {
            ecs.updateElementIndex($(this), 'investigator', ecs.partbNo - 1);
          });

          // reset entry fields
          $('#tabs-' + tabNo).find('input,select,textarea,label').each(function() {
            var elem = $(this);
            if (elem.is('input:checkbox') || elem.is('input:radio')) {
              elem.attr('checked', false);
            } else {
              elem.val('');
            }
          });

          // update count
          $('#id_investigator-TOTAL_FORMS').val(ecs.partbNo);

          // show numbers
          $('div #tabs-' + tabNo + ' span.partbno').html('Zentrum ' + ecs.partbNo);
          if (ecs.partbNo == 2) {
            $('div #tabs-' + (tabNo - 1) + ' span.partbno').html('Zentrum 1');
          }
          return false;
        });


        /* Part B remove */
        $('.partb_remove').click(function() {
          if (ecs.partbNo < 2) {
            alert('Mehr darf nicht! (Und diese Meldung sollte nie angezeigt werden)');
            return false;
          }
          // TODO some warning, because entered data might get lost
          // TODO better disable than delete
          // TODO these ops remove the LAST not CURRENT tab, change this
          $('.tab_headers li:last').remove();
          var tabNo = ecs.partbNo + ecs.partbOffset;
          $('div #tabs-' + tabNo).remove();
          ecs.partbNo--;
          return false;
        });
    
    }); 

})(jQuery);