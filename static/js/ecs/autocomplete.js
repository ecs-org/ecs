var ecs = window.ecs = window.ecs || {};
ecs.autocomplete = {};

ecs.autocomplete.Autocompleter = new Class({
    Implements: Events,
    initialize: function(input, options){
        this.element = new Element('div', {'class': 'ecs-Autocomplete'});
        this.textInput = new Element('input', {type: 'text', value: input.value});
        this.textInput.addEvent('focus', this.activate.bind(this));
        this.textInput.addEvent('blur', (function(){
            setTimeout(this.deactivate.bind(this), 200);
        }).bind(this));
        this.textInput.addEvent('keydown', this.onKeyDown.bind(this));
        this.input = new Element('input', {type: 'hidden', value: input.value, name: input.name});
        this.choiceBox = new Element('div', {'class': 'choices'});
        this.choiceBox.hide();
        this.choiceBox.addEvent('click', this.onChoiceBoxClick.bind(this));
        this.element.adopt(this.input, this.textInput, this.choiceBox);
        this.maxVisibleChoices = options.maxVisibleChoices || 10;
        this.choices = [];
        this.filteredElements = [];
        this.highlightChoiceIndex = -1;
        this.url = options.url || input.getProperty('x-autocomplete-url');
        this.active = false;
        this.lastFilter = '';
        if(this.url){
            var request = new Request.JSON({
                url: this.url,
                onSuccess: (function(result){
                    this.setChoices(result);
                }).bind(this)
            });
            request.send();
        }
        else if(options.choices){
            this.setChoices(options.choices);
        }
        this.element.replaces(input);
    },
    renderChoice: function(choice){
        return new Element('div', {html: choice[1]});
    },
    getChoiceText: function(choice){
        return choice[2];
    },
    getChoiceValue: function(choice){
        return choice[0];
    },
    setChoices: function(choices){
        this.choices = choices;
        choices.each(function(c){
            var el = this.renderChoice(c);
            el.store('ecs-Autocomplete-choice', c);
            this.choiceBox.grab(el);
        }, this);
    },
    selectChoice: function(c){
        if(this.currentChoiceElement){
            this.currentChoiceElement.removeClass('selected');
        }
        this.textInput.value = this.getChoiceText(c);
        this.input.value = this.getChoiceValue(c);
        this.currentChoice = c;
    },
    onChoiceBoxClick: function(e){
        var c = $(e.target).retrieve('ecs-Autocomplete-choice');
        if(!c){
            return;
        }
        this.selectChoice(c);
        this.deactivate();
        return false;
    },
    getChoiceForElement: function(el){
        return el.retrieve('ecs-Autocomplete-choice');
    },
    filterChoices: function(text){
        text = text.toLowerCase();
        if(text == this.lastFilter){
            return;
        }
        var refine = text.indexOf(this.lastFilter) === 0 && this.filteredElements.length;
        var baseElements = refine ? this.filteredElements : this.choiceBox.getChildren();
        this.filteredElements = [];
        this.highlightChoiceIndex = -1;
        baseElements.each(function(el){
            var c = this.getChoiceForElement(el);
            if(this.maxVisibleChoices > this.filteredElements.length && this.getChoiceText(c).toLowerCase().indexOf(text) === 0){
                this.filteredElements.push(el);
                el.show();
            }
            else{
                el.hide();
            }
        }, this);
        if(this.filteredElements.length == 1){
            this.selectChoice(this.getChoiceForElement(this.filteredElements[0]));
        }
        this.lastFilter = text;
    },
    activate: function(){
        if(this.active){
            return;
        }
        this.active = true;
        this.filterChoices(this.textInput.value);
        this.choiceBox.show();
        this.interval = setInterval(this.tick.bind(this), 333);
    },
    tick: function(){
        this.filterChoices(this.textInput.value);
    },
    deactivate: function(){
        if(!this.active){
            return;
        }
        this.choiceBox.hide();
        clearInterval(this.interval);
        this.active = false;
    },
    highlight: function(index){
        if(this.highlightChoiceIndex != -1){
            this.filteredElements[this.highlightChoiceIndex].removeClass('highlight');
        }
        if(index != -1){
            this.highlightChoiceIndex = index % this.filteredElements.length;
            this.filteredElements[this.highlightChoiceIndex].addClass('highlight');
        }
        else{
            this.highlightChoiceIndex = -1;
        }
    },
    onKeyDown: function(e){
        if(e.key == 'esc'){
            this.textInput.blur();
            return false;
        }
        if(e.key == 'down'){
            this.highlight(this.highlightChoiceIndex + 1);
            return false;
        }
        if(e.key == 'up'){
            this.highlight(this.highlightChoiceIndex - 1);
            return false;
        }
        if(e.key == 'enter'){
            if(this.highlightChoiceIndex != -1){
                var choice = this.getChoiceForElement(this.filteredElements[this.highlightChoiceIndex]);
                this.selectChoice(choice);
                this.deactivate();
                return false;
            }
        }
        this.activate();
    }
});