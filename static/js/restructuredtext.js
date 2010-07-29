window.ReST = new Class({
    initialize: function(textarea){
        this.textarea = $(textarea);
    },
    
    makeBold: function(){
        this.textarea.insertAroundCursor({before: '**', after: '**'})
    },
    
    makeItalic: function(){
        this.textarea.insertAroundCursor({before: '*', after: '*'});
    },
    
    makeHeading: function(){
        var text = this.textarea.getSelectedText().trim();
        if(text){
            this.textarea.insertAtCursor("\n\n" + text + "\n" + "~".repeat(text.length) + "\n");
        }
        else{
            this.textarea.insertAroundCursor({after: '~~~~~~~~~~~~~~~~~~'});
        }

    }

});

