ecs.pdfviewer.Controller = new Class({
    initialize: function(imageSet, x, y, options){
        this.imageSet = imageSet;
        this.x = x;
        this.y = y;
        this.sliceLength = x * y;
        this.options = options || {'showAnnotations': true};
    },
    getBlockIndex: function(pageIndex){
        return parseInt(Math.floor(pageIndex / this.sliceLength));
    },
    render: function(viewer, pageIndex, force){
        viewer.render(this.imageSet, this.getBlockIndex(pageIndex) * this.sliceLength, this.x, this.y);
    }
});

ecs.pdfviewer.DocumentViewer = new Class({
    initialize: function(el, options){
        this.element = $(el);
        this.pageCount = options.pageCount;
        this.controllers = options.controllers;
        this.wheelScrollThreshold = options.wheelScrollThreshold || 1.0;
        this.wheelTimeThreshold = options.wheelTimeThreshold || 1;
        this.title = options.title;
        this.helpContents = options.helpContents;
        this.searchURL = options.searchURL;
        this.editAnnotationURL = options.editAnnotationURL;
        this.deleteAnnotationURL = options.deleteAnnotationURL;
        this.metaKey = options.metaKey || '';
        this.minAnnotationWidth = options.minAnnotationWidth || 20;
        this.minAnnotationHeight = options.minAnnotationHeight || 20;

        this.shortcuts = options.shortcuts;
        this.keyboardNavigationEnabled = true;
        this.scrollFx = new Fx.Scroll(document.body, {duration: 100});

        this.imageSets = {};
        this.currentPageIndex = 0;
        this.currentControllerIndex = 0;
        this.currentScreen = null;
        this.currentRenderArgs = [];

        this._wheelCounter = 0;
        this._wheelTimeout = null;
        this._wheelTimestamp = null;
        this._wheelReset = (function(){this._wheelCounter = 0; this._wheelTimeout = null; this._wheelTimestamp = null;}).bind(this);
        $(window).addEvent('click', this.handleClick.bind(this));
        $(window).addEvent('mousewheel', this.handleMouseWheel.bind(this));
        $(window).addEvent('keydown', this.handleKeyPress.bind(this));
        
        this.body = new Element('div', {'class': 'body'});
        this.viewport = new Element('div', {'class': 'viewport'});
        this.header = new Element('div', {'class': 'header', html: this.title});
        this.menuButton = new Element('a', {id: 'menubutton', html: '❀', events: {click: this.toggleMenu.bind(this)}});
        this.prevLink = new Element('a', {'class': 'previous', title: 'previous page'});
        this.nextLink = new Element('a', {'class': 'next', title: 'next page'});
        this.element.adopt(this.header, this.menuButton, this.body);
        this.body.adopt(this.prevLink, this.viewport, this.nextLink);

        this.prevLink.addEvent('click', (function(){
            this.previousPage();
        }).bind(this));
        this.nextLink.addEvent('click', (function(){
            this.nextPage();
        }).bind(this));

        this.annotations = $H({});
        this.annotationMode = false;
        this.annotationOverlay = new Element('div', {'class': 'annotationOverlay'})
        this.annotationFrame = new ecs.dragdrop.Frame(this.annotationOverlay);
        
        this.annotationFrame.addEvent('complete', (function(f){
            if(f.w > this.minAnnotationWidth || f.h > this.minAnnotationHeight){
                var rel = this.annotationOverlay.getCoordinates();
                var annotation = new ecs.pdfviewer.Annotation(null, "", f.x / rel.width, f.y / rel.height, f.w / rel.width, f.h / rel.height);
                this.addAnnotation(this.currentPageIndex, annotation);
                var pageEl = this.currentScreen.getElement('.page');
                var annotationElement = this.renderAnnotation(pageEl, annotation);
                annotation.startAnnotationMode(annotationElement);
                this.annotationEditor.show(annotation, annotationElement);
            }
        }).bind(this));

        this.annotationEditor = new ecs.pdfviewer.AnnotationEditor(this);
        this.searchPopup = new ecs.pdfviewer.SearchPopup(this);
        this.gotoPagePopup = new ecs.pdfviewer.GotoPagePopup(this);
        this.menuPopup = new ecs.pdfviewer.MenuPopup(this);
        
        [this.annotationEditor, this.searchPopup, this.gotoPagePopup, this.menuPopup].each(function(popup){
            popup.addEvent('show', (function(){
                this.keyboardNavigationEnabled = false;
                this.currentPopup = popup;
            }).bind(this));
            popup.addEvent('hide', (function(){
                this.keyboardNavigationEnabled = true;
                this.currentPopup = null;
            }).bind(this));
        }, this);

    },
    gotoAnchor: function(hash){
        hash = hash || window.location.hash;
        if(hash){
            this.setPage(parseInt(hash.substring(1)) - 1, false);
            this.setControllerIndex(this.controllers.length - 1);
        }
    },
    scrollToTop: function(){
        this.scrollFx.toTop();
        return true;
    },
    scrollToBottom: function(){
        this.scrollFx.toBottom();
        return true;
    },
    setMetaKey: function(meta){
        this.metaKey = meta;

        var request = new Request({
            url: window.location.href,
            method: 'post',
            data: 'metaKey=' + this.metaKey,
            onSuccess: function(){},
        });
        request.send();
    },
    getImageSetKey: function(x, y){
        return x + 'x' + y;
    },
    addImageSet: function(imageSet){
        var key = this.getImageSetKey(imageSet.sprite.x, imageSet.sprite.y);
        this.imageSets[key] = imageSet;
    },
    addImage: function(image){
        var imageSet = this.imageSets[this.getImageSetKey(image.tx, image.ty)];
        if(!imageSet){
            dbug.log("dropping image: ", image);
            return;
        }
        imageSet.addImage(image);
    },
    getController: function(){
        return this.controllers[this.currentControllerIndex];
    },
    update: function(){
        this.getController().render(this, this.currentPageIndex);
    },
    setControllerIndex: function(index){
        this.currentControllerIndex = index;
        this.update();
    },
    cycleController: function(delta){
        index = (this.controllers.length + this.currentControllerIndex + (delta || 1)) % this.controllers.length
        this.setControllerIndex(index);
    },
    setPage: function(pageIndex, update){
        if(pageIndex < 0 || pageIndex >= this.pageCount){
            return false;
        }
        if(pageIndex != this.currentPageIndex){
            this.currentPageIndex = pageIndex;
            if(update !== false){
                this.update();
            }
            return true;
        }
        return false;
    },
    nextPage: function(delta){
        if(this.setPage(Math.min(this.currentPageIndex + (delta || this.getController().sliceLength), this.pageCount - 1))){
            this.scrollToTop();
        }
        return true;
    },
    previousPage: function(delta){
        if(this.setPage(Math.max(this.currentPageIndex - (delta || this.getController().sliceLength), 0))){
            this.scrollToBottom();
        }
        return true;
    },
    getCurrentBlockIndex: function(){
        return this.getController().getBlockIndex(this.currentPageIndex);
    },
    selectPage: function(delta){
        var oldBlockIndex = this.getCurrentBlockIndex();
        this.setPage(this.currentPageIndex + delta, false);
        if(oldBlockIndex != this.getCurrentBlockIndex()){
            this.update();
        }
        else{
            this.currentScreen.getElement('.page.current').removeClass('current');
            var el = this.currentScreen.getElement('.page' + this.currentPageIndex);
            el.addClass('current');
            if(this.getController().sliceLength == 1){
                if(delta > 0){
                    this.scrollFx.toTop();
                }
                else{
                    this.scrollFx.toBottom();
                }
            }
            else{
                this.scrollFx.toElement(el);
            }
        }
        return true;
    },
    selectNextPage: function(){
        return this.selectPage(+1);
    },
    selectPreviousPage: function(){
        return this.selectPage(-1);
    },
    selectPreviousRow: function(){
        return this.selectPage(-this.getController().x);
    },
    selectNextRow: function(){
        return this.selectPage(this.getController().x);
    },
    gotoPage: function(pageIndex){
        this.setPage(pageIndex, false);
        this.setControllerIndex(this.controllers.length - 1);
    },
    addAnnotation: function(pageIndex, annotation){
        var key = '_' + pageIndex;
        if(!this.annotations[key]){
            this.annotations[key] = [];
        }
        this.annotations[key].push(annotation);
    },
    removeAnnotation: function(annotationElement){
        var annotation = annotationElement.retrieve('annotation');
        this.annotations.each(function(annotations){
            annotations.erase(annotation);
        });
        if(this.annotationMode){
            annotation.endAnnotationMode(annotationElement);
        }
        annotationElement.dispose();
        if(!annotation.pk){
            return;
        }
        var request = new Request({
            url: this.deleteAnnotationURL,
            method: 'post',
            data: 'pk=' + annotation.pk
        });
        request.send();
    },
    sendAnnotationUpdate: function(annotation){
        var request = new Request({
            url: this.editAnnotationURL,
            method: 'post',
            data: $H({
                pk: annotation.pk,
                x: annotation.x,
                y: annotation.y,
                width: annotation.w,
                height: annotation.h,
                text: annotation.text,
                page_number: this.currentPageIndex + 1
            }).toQueryString()
        });
        request.send();
    },
    getAnnotations: function(pageIndex){
        return this.annotations['_' + pageIndex] || [];
    },
    renderAnnotation: function(pageEl, annotation){
        var annotationElement = annotation.attachTo(pageEl, (function(){
            this.annotationEditor.show(annotation, annotationElement);
        }).bind(this));
        annotationElement.store('annotation', annotation);
        return annotationElement;
    },
    render: function(imageSetKey, offset, w, h){
        if($A(arguments).every((function(val, i){ return val == this.currentRenderArgs[i]}).bind(this))){
            return;
        }
        this.currentRenderArgs = $A(arguments);
        window.location.hash = this.currentPageIndex + 1;
        this.header.innerHTML = this.title + ' <span class="location">Seite ' + (offset + 1) + (w*h > 1 ? '–' + (offset + w*h) : '') + ' von ' + this.pageCount + '</span>';
        var imageSet = this.imageSets[imageSetKey];
        if(this.currentScreen){
            this.currentScreen.dispose();
        }
        var screen = new Element('div', {'class': 'screen i' + imageSetKey});
        var currentPageElement = null;
        for(var y = 0; y < h; y++){
            var row = new Element('div', {'class': 'row'});
            for(var x = 0; x < w; x++){
                var pageIndex = offset + y*w + x;
                if(pageIndex >= this.pageCount){
                    break;
                }
                var pageEl = imageSet.renderPage(pageIndex, (function(pageEl){
                    this.getAnnotations(pageEl.retrieve('pageIndex')).each((function(annotation){
                        this.renderAnnotation(pageEl, annotation);
                    }).bind(this));
                }).bind(this));
                pageEl.addClass('page');
                pageEl.addClass('page' + pageIndex);
                pageEl.id = 'p' + imageSetKey + '_' + pageIndex;
                if(pageIndex == this.currentPageIndex){
                    pageEl.addClass('current');
                    currentPageElement = pageEl;
                }
                pageEl.grab(new Element('div', {'class': 'info', html: 'Seite ' + (pageIndex + 1)}));
                row.grab(pageEl);
            }
            screen.grab(row);
        }
        this.viewport.grab(screen);
        this.currentScreen = screen;
        this.scrollFx.toElement(currentPageElement);
        return screen;
    },
    toggleAnnotationMode: function(){
        var controller = this.getController();
        if(controller.sliceLength != 1){
            return false;
        }
        var am = this.annotationMode = !this.annotationMode;
        var pageEl = this.currentScreen.getElement('.page');
        this.nextLink.setStyle('display', am ? 'none' : '');
        this.prevLink.setStyle('display', am ? 'none' : '');
        pageEl[am ? 'appendChild' : 'removeChild'](this.annotationOverlay);
        if(!this.annotationMode){
            pageEl.getChildren('.annotation').each((function(annotationElement){
                var annotation = annotationElement.retrieve('annotation');
                annotation.endAnnotationMode(annotationElement);
            }).bind(this));
        }
        else{
            pageEl.getChildren('.annotation').each(function(annotationElement){
                var annotation = annotationElement.retrieve('annotation');
                annotation.startAnnotationMode(annotationElement);
            });
        }
        return true;
    },
    quitAnnotationMode: function(){
        if(this.annotationMode){
            this.toggleAnnotationMode();
            return true;
        }
        return false;
    },
    toggleHelp: function(){
        this.helpContents.toggleClass('hidden');
        return true;
    },
    toggleMenu: function(){
        this.menuPopup.toggle();
        return true;
    },
    showPopup: function(popup){
        if(this.currentPopup){
            this.currentPopup.hide();
        }
        this.helpContents.addClass('hidden');
        popup.show();
        return true;
    },
    showSearch: function(){
        return this.showPopup(this.searchPopup);
    },
    showGotoPage: function(){
        return this.showPopup(this.gotoPagePopup);
    },
    cycleIn: function(){
        this.cycleController(+1);
        return true;
    },
    cycleOut: function(){
        this.cycleController(-1);
        return true;
    },
    firstPage: function(){
        this.setPage(0);
        return true;
    },
    lastPage: function(){
        this.setPage(this.pageCount - 1);
        return true;
    },
    handleKeyPress: function(e){
        if(!this.keyboardNavigationEnabled){
            return true;
        }
        var metaKey = !this.metaKey || e[this.metaKey];
        var U = ecs.pdfviewer.utils;
        var atTop = U.isAtTop();
        var atBottom = U.isAtBottom();
        
        for(var i=0;i<this.shortcuts.length;i++){
            var s = this.shortcuts[i];
            if(this.annotationMode && !s.annotationMode){
                continue;
            }
            if(s.key == 'pagedown' && e.code != ecs.pdfviewer.utils.PAGE_DOWN || s.key == 'pageup' && e.code != ecs.pdfviewer.utils.PAGE_UP){
                continue;
            }
            else if(s.key && e.key != s.key){
                continue;
            }
            if(typeof(s.shift) != 'undefined' && s.shift != e.shift || this.metaKey && !!s.meta != metaKey){
                continue;
            }
            if(s.top && !atTop || s.bottom && !atBottom){
                continue;
            }
            if(this[s.command]()){
                return false;
            }
        }
    },
    handleMouseWheel: function(e){
        if(this.annotationMode){
            return true;
        }
        
        var U = ecs.pdfviewer.utils;
        if(e.wheel > 0 && U.isAtTop() || e.wheel < 0  && U.isAtBottom()){
            if(this._wheelTimeout){
                clearTimeout(this._wheelTimeout)
            }
            else{
                this._wheelTimestamp = (new Date()).getTime();
            }
            this._wheelTimeout = setTimeout(this._wheelReset, 100);
            this._wheelCounter += Math.abs(e.wheel);
            var scrollTime = (new Date()).getTime() - this._wheelTimestamp;
            if(this._wheelCounter >= this.wheelScrollThreshold && scrollTime >= this.wheelTimeThreshold){
                this._wheelCounter = 0;
                this._wheelTimestamp = 0;
                if(e.wheel > 0){
                    this.previousPage();
                }
                else if(e.wheel < 0){
                    this.nextPage();
                }
            }
        }
    },
    handleClick: function(e){
        var target = $(e.target);
        var pageEl = target.hasClass('page') ? target : target.getParent('.page');
        if(this.annotationMode){
            return;
        }
        if(e.alt){
            this.cycleController(e.shift ? -1 : +1);
            return false;
        }
        if(pageEl){
            this.gotoPage(pageEl.retrieve('pageIndex'));
        }
    }
});
