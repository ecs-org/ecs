ecs.textarea.toolbarItems = {};

ecs.textarea.toolbarItems.boilerplate = function(label, url){
    return function(textarea){
        var button = new Element('a', {title: label, 'class': 'boilerplate'});
        textarea.addEvent('keydown', function(e){
            if(e.alt && e.key == 'm'){
                button.fireEvent('click');
                return false;
            }
        });
        button.addEvent('click', function(){
            var status = {value: textarea.getSelectedText()};
            var container = new Element('div', {'class': 'boilerplate_selector'});
            var searchInput = new Element('input', {type: 'text', value: status.value});
            var resultList = new Element('div', {'class': 'resultlist'});
            container.grab(searchInput);
            container.grab(resultList);
            textarea.grab(container, 'before');
            var dispose = function(){
                window.removeEvent('click', dispose);
                clearInterval(status.interval);
                container.dispose();
            };
            var insert = function(text){
                dispose();
                textarea.focus();
                textarea.insertAtCursor(text);
                textarea.fireEvent('change');
            };
            var update = function(q, initial){
                var request = new Request.JSON({
                    url: url + '?q=' + encodeURIComponent(q),
                    onSuccess: function(results){
                        if(initial){
                            if(results.length == 1){
                                insert(results[0].text);
                                return;
                            }
                            window.addEvent('click', dispose);
                            container.setStyle('display', 'block');
                            searchInput.focus();
                        }
                        resultList.innerHTML = '';
                        results.each(function(text){
                            var display = new Element('a', {html: '<strong>{slug}</strong>: {text}'.substitute(text)})
                            display.addEvent('click', function(){
                                insert(text.text);
                                return false;
                            });
                            resultList.grab(display);
                        });
                    }
                });
                request.send();
            };
            update(textarea.getSelectedText(), true);
            searchInput.addEvent('keydown', function(e){
                if(e.key == 'enter'){
                    update(searchInput.value, true);
                    return false;
                }
                if(e.key == 'esc'){
                    dispose();
                }
            });
            status.interval = setInterval(function(){
                if(searchInput.value != status.value){
                    status.value = searchInput.value;
                    update(searchInput.value);
                }
            }, 500);
        });
        return button;
    };
};

ecs.textarea.toolbarItems.annotations = function(label, url){
    return function(textarea){
        var button = new Element('a', {title: label, 'class': 'annotations'});
        button.addEvent('click', function(){
            var popup = new ecs.widgets.Popup({url: url});
            popup.addEvent('load', function(){
                var copyButton = new Element('input', {type: 'submit', value: "Kopieren"});
                copyButton.addEvent('click', function(){
                    var text = "";
                    popup.element.getElements('input[type=checkbox]').each(function(checkbox){
                        if(checkbox.checked){
                            var a = checkbox.getParent('.annotation');
                            text += a.getElement('.copytext').innerHTML + '\n\n';
                        }
                    });
                    textarea.insertAtCursor(text);
                    textarea.fireEvent('change');
                    popup.dispose();
                    return false;
                });
                popup.element.grab(copyButton);
            });
            return false;
        });
        return button;
    };
};

ecs.textarea.toolbarItems.versionHistory = function(label, url){
    return function(textarea){
        var button = new Element('a', {title: label, html: label, 'class': 'versions'});
        button.addEvent('click', function(){
            var popup = new ecs.widgets.Popup({
                url: url + '?field=' + textarea.name
            });
        });
        return button;
    };
};

