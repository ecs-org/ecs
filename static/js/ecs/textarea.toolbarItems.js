ecs.textarea.toolbarItems = {};

ecs.textarea.toolbarItems.boilerplate = function(label, url) {
    return function(textarea) {
        var button = jQuery('<a>', {
            title: label,
            'class': 'boilerplate',
            click: function(ev) {
                ev.preventDefault();
                var status = {
                    value: textarea.val().slice(
                        textarea.prop('selectionStart'),
                        textarea.prop('selectionEnd'))
                };
                var container = jQuery('<div>', {'class': 'boilerplate_selector'});
                var searchInput = jQuery('<input>', {type: 'text', value: status.value});
                var resultList = jQuery('<div>', {'class': 'resultlist'});
                container.append(searchInput);
                container.append(resultList);
                jQuery(textarea).before(container);
                var dispose = function() {
                    jQuery(window).off('click', dispose);
                    clearInterval(status.interval);
                    container.remove();
                };
                var insert = function(text) {
                    dispose();
                    textarea.focus();
                    var v = textarea.val();
                    var s = textarea.prop('selectionStart');
                    var e = textarea.prop('selectionEnd');
                    textarea.val(v.slice(0, s) + text + v.slice(e, -1));
                    textarea.prop('selectionStart', s);
                    textarea.prop('selectionEnd', s + text.length);
                };
                var update = function(q, initial) {
                    jQuery.get({
                        url: url + '?q=' + encodeURIComponent(q),
                        headers: {'X-CSRFtoken': Cookie.read('csrftoken')},
                        dataType: 'json',
                        success: function(results){
                            if(initial){
                                if(results.length == 1){
                                    insert(results[0].text);
                                    return;
                                }
                                jQuery(window).click(dispose);
                                container.css('display', 'block');
                                searchInput.focus();
                            }
                            resultList.html('');
                            results.each(function(text) {
                                var display = jQuery('<a>', {
                                    html: '<strong>{slug}</strong>: {text}'.substitute(text),
                                    click: function(ev) {
                                        ev.preventDefault();
                                        insert(text.text);
                                    }
                                });
                                resultList.append(display);
                            });
                        }
                    });
                };
                update(status.value, true);
                searchInput.keydown(function(ev) {
                    if(ev.key == 'Enter'){
                        ev.preventDefault();
                        update(searchInput.val(), true);
                    }
                    if(ev.key == 'Escape'){
                        ev.preventDefault();
                        dispose();
                    }
                });
                status.interval = setInterval(function(){
                    if(searchInput.val() != status.value){
                        status.value = searchInput.val();
                        update(searchInput.val());
                    }
                }, 500);
            }
        });
        textarea.keydown(function(ev) {
            if (ev.altKey && ev.key == 'm') {
                ev.preventDefault();
                button.click();
            }
        });
        return button;
    };
};

ecs.textarea.toolbarItems.versionHistory = function(label, url){
    return function(textarea) {
        return jQuery('<a>', {
            title: label,
            'class': 'versions',
            click: function(ev) {
                ev.preventDefault();
                ecs.fieldhistory.show(url, textarea.attr('name'));
            }
        });
    };
};

