ecs.pdfviewer.Popup = new Class({
    Implements: Events,

    initialize: function(viewer){
        this.viewer = viewer;
        this.dispose = this.dispose.bind(this);
    },
    init: function(){
        if(this.element){
            return;
        }
        this.cover = new Element('div', {'class': 'cover'});
        this.element = new Element('div', {'class': 'searchPopup annotationDisplay popup'});
        var background = new Element('div', {'class': 'background'});
        var content = new Element('div', {'class': 'content'});
        var closeButton = new Element('a', {'class': 'close', 'html': '&times;'});
        this.element.grab(background);
        this.element.grab(content);
        this.element.grab(closeButton);

        this.initContent(content);
        
        closeButton.addEvent('click', this.dispose);
        this.escapeListener = (function(e){
            if(e.key == 'esc'){
                this.dispose();
                return false;
            }
        }).bind(this);
        this.cover.setStyle('display', 'none');
        this.cover.grab(this.element);
        $(document.body).grab(this.cover);
        new Drag.Move(this.element, {handle: background});
        this.visible = false;
    },
    dispose: function(){
        $(document.body).removeEvent('keydown', this.escapeListener);
        this.cover.setStyle('display', 'none');
        this.visible = false;
        this.fireEvent('hide');
    },
    show: function(){
        this.init();
        this.cover.setStyle('display', '');
        this.visible = true;
        this.onShow.apply(this, arguments);
        $(document.body).addEvent('keydown', this.escapeListener);
        this.fireEvent('show');
    },
    toggle: function(){
        if(!this.visible){
            this.show();
        }
        else{
            this.dispose();
        }
    },
    onShow: function(){},
    initContent: function(content){}
});

ecs.pdfviewer.MenuPopup = new Class({
    Extends: ecs.pdfviewer.Popup,
    
    initialize: function(viewer){
        this.parent(viewer);
    },
    
    makeMenuButton: function(item){
        var button = new Element('a', {html: item.label});
        button.addEvent('click', (function(e){
            this.dispose();
            if(item.command){
                this.viewer[item.command]();
            }
            e.stop();
            return false;
        }).bind(this));
        return button;
    },
    
    initContent: function(content){
        this.element.addClass('menu');
        var menuItems = [
            {label: 'first', command: 'firstPage'},
            {label: 'goto', command: 'showGotoPage'},
            {label: 'zoom', command: 'cycleIn'},
            {label: 'annotate/leave annotate', command: 'toggleAnnotationMode'},
            {label: 'exit', command: ''},
            {label: 'search', command: 'showSearch'},
            {label: 'help', command: 'toggleHelp'},
            {label: 'share', command: 'shareAnnotations'},
            {label: 'last', command: 'lastPage'}
        ];
        menuItems.each(function(item){
            content.grab(this.makeMenuButton(item));
        }, this);
    },
    
    show: function(){
        if(Browser.Features.Touch){
            this.init();
            var touchStop = new Element('div', {'class': 'touchStop'});
            this.element.grab(touchStop);
            $(document.body).addEvent('touchend', function(){
                touchStop.dispose();
            });
        }
        this.parent();
    }
});

ecs.pdfviewer.GotoPagePopup = new Class({
    Extends: ecs.pdfviewer.Popup,
    
    initialize: function(viewer){
        this.parent(viewer);
        this.onKeyDown = this.onKeyDown.bind(this);
    },
    
    initContent: function(content){
        this.element.addClass('gotoPage');
        this.input = new Element('input', {type: 'text'}); // type: 'number', min: '1', max: this.viewer.pageCount
        this.input.addEvent('change', (function(){
            var p = parseInt(this.input.value);
            this.viewer.gotoPage(p - 1);
        }).bind(this));
        this.input.addEvent('keydown', this.onKeyDown);
        content.grab(new Element('span', {'class': 'label', 'html': 'Goto Page:'}))
        content.grab(this.input);
    },
    onShow: function(){
        this.input.value = this.viewer.currentPageIndex + 1;
        this.input.focus();
        this.input.selectRange(0, this.input.value.length);
    },
    onKeyDown: function(e){
        if(e.key == 'enter'){
            this.input.blur();
            this.dispose();
            e.stop();
        }
    }
});

ecs.pdfviewer.AnnotationSharingPopup = new Class({
    Extends: ecs.pdfviewer.Popup,
    
    initContent: function(content){
        this.element.addClass('annotationSharing');
        this.widget = new ecs.widgets.Widget(content);
    },
    onShow: function(){
        this.widget.load('annotations/share/');
    }
});

ecs.pdfviewer.SearchPopup = new Class({
    Extends: ecs.pdfviewer.Popup,
    
    initContent: function(content){
        this.element.addClass('search');
        this.input = new Element('input', {type: 'text', value: ''});
        this.input.addEvent('keypress', (function(e){
            if(e.key == 'enter'){
                this.search();
                return false;
            }
        }).bind(this));
        var searchLink = new Element('a', {html: 'Search'});
        searchLink.addEvent('click', (function(){
            this.search();
        }).bind(this));
        this.resultList = new Element('div', {'class': 'results'});
        content.grab(this.input);
        content.grab(searchLink);
        content.grab(this.resultList);
    },
    search: function(){
        var popup = this;
        var request = new Request.JSON({
            url: this.viewer.searchURL,
            data: $H({q: this.input.value}).toQueryString(),
            method: 'get',
            onSuccess: (function(results){
                this.resultList.innerHTML = results.length ? '' : '<i>No results.</i>';
                results.each((function(result){
                    var el = new Element('div', {'html': '<span class="pageNumber">Seite ' + result.page_number + '</span>: ' + result.highlight});
                    el.addEvent('click', function(){
                        popup.viewer.gotoPage(result.page_number - 1);
                    });
                    this.resultList.grab(el);
                }).bind(this));
            }).bind(this)
        });
        request.send();
    },
    onShow: function(query){
        if(typeof(query) !== 'undefined'){
            this.input.value = query;
        }
        this.input.focus();
    }
});

ecs.pdfviewer.AnnotationEditor = new Class({
    Extends: ecs.pdfviewer.Popup,
    initContent: function(content){
        this.textarea = new Element('textarea', {html: this.text});
        this.authorInfo = new Element('div', {'class': 'authorInfo'});
        var saveLink = new Element('a', {html: 'Save'});
        var cancelLink = new Element('a', {html: 'Cancel'});
        var deleteLink = new Element('a', {html: 'Delete'});
        content.grab(this.authorInfo);
        content.grab(this.textarea);
        content.grab(saveLink);
        content.grab(cancelLink);
        content.grab(deleteLink);
        saveLink.addEvent('click', this.onSave.bind(this));
        cancelLink.addEvent('click', this.onCancel.bind(this));
        deleteLink.addEvent('click', this.onDelete.bind(this));
        this.addEvent('hide', (function(){
            this.annotation = null;
        }).bind(this));
    },
    onShow: function(annotation, element){
        this.annotation = annotation;
        this.annotationElement = element;
        this.textarea.value = annotation.text;
        this.element.toggleClass('foreign', !!annotation.author);
        this.authorInfo.innerHTML = 'Anmerkung von ' + annotation.author + ':';
        this.textarea.focus();
    },
    onSave: function(){
        if(this.annotation.text != this.textarea.value){
            this.annotation.text = this.textarea.value;
            this.annotation.author = null;
            this.annotationElement.removeClass('foreign');
            this.viewer.sendAnnotationUpdate(this.annotation);
        }
        this.dispose();
    },
    onCancel: function(){
        this.dispose();
    },
    onDelete: function(){
        this.viewer.removeAnnotation(this.annotationElement);
        this.dispose();
    }
});
