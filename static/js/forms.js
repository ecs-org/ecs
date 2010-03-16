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
            if(maxlength){
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

    $(function(){
        if(!$('.tab_headers > li.active').length && !window.location.hash){
            $(".tab_headers > li:first-child").addClass('active');
        }
        $(".tab_headers").tabify();
        ecs.setupFormFieldHelpers();
    
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
    
    }); 

})(jQuery);