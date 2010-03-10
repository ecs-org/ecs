var ecs = {};

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


jQuery(function($){    
    ecs.setupFormFieldHelpers();
});