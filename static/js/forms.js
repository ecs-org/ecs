var ecs = {};

jQuery(function($){
    $('form .field.DateField > input').datepicker({dateFormat: 'dd.mm.yy'});    
    
    $('form .field').each(function(){
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
    });
    
    var formControls = $('form .field input, form .field textarea, form .field select');
    formControls.focus(function(){
        $(this).parent('.field').addClass('focus');
    });
    formControls.blur(function(){
        $(this).parent('.field').removeClass('focus');
    });
    
});