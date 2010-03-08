var ecs = {};

jQuery(function($){
    $('form ol li.DateField > input').datepicker({dateFormat: 'dd.mm.yy'});    
    
    $('form ol li').each(function(){
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
    
    var formControls = $('form ol li input, form ol li textarea, form ol li select');
    formControls.focus(function(){
        $(this).parent('li').addClass('focus');
    });
    formControls.blur(function(){
        $(this).parent('li').removeClass('focus');
    });
    
});