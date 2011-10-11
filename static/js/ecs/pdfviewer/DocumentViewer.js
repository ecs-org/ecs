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
    render: function(viewer, pageIndex, options){
        viewer.render(this.imageSet, this.getBlockIndex(pageIndex) * this.sliceLength, this.x, this.y, options);
    },
    getSize: function(){
        return this.x * this.y;
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
        this.searchURL = options.searchURL;
        this.editAnnotationURL = options.editAnnotationURL;
        this.deleteAnnotationURL = options.deleteAnnotationURL;
        this.helpURL = options.helpURL;
        this.metaKey = options.metaKey || '';
        this.minAnnotationWidth = options.minAnnotationWidth || 20;
        this.minAnnotationHeight = options.minAnnotationHeight || 20;
        this.swipeDistance = options.swipeDistance || 30;
        this.touchholdDelay = options.touchholdDelay || 300;
        this.pinchThreshold = options.pinchThreshold || 0.4
        this.touchCenterSize = options.touchCenterSize || 20;

        this.shortcuts = options.shortcuts || [];
        this.gestures = options.gestures || [];
        this.keyboardNavigationEnabled = true;
        this.gestureNavigationEnabled = true;
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

        this.element.store('swipe:distance', this.swipeDistance);
        this.element.addEvent('swipe', this.handleSwipe.bind(this));
        this.element.store('touchhold:delay', this.touchholdDelay);
        this.element.addEvent('touchhold', this.handleTouchhold.bind(this));
        this.element.store('pinch:threshold', this.pinchThreshold);
        this.element.addEvent('pinch', this.handlePinch);
        
        if(Browser.Features.Touch){
            this.element.addEvent('click', (function(e){
                if(this.getController().getSize() != 1){
                    return;
                }
                var size = this.element.getSize();
                if(Math.abs(e.page.x - size.x/2) <= this.touchCenterSize / 2 && Math.abs(e.page.y - size.y/2) < this.touchCenterSize / 2){
                    return this.toggleMenu();
                }
            }).bind(this));
        }
        
        this.viewport = new Element('div', {'class': 'viewport'});
        this.innerViewport = new Element('div');
        this.viewport.grab(this.innerViewport);
        this.viewportOffset = 0;
        this.viewportAnimated = false;
        
        this.body = new Element('div', {'class': 'body'});
        this.header = new Element('div', {'class': 'header', html: this.title});
        this.header.addEvent('click', this.toggleMenu.bind(this));
        this.menuButton = new Element('a', {id: 'menubutton', html: '❀'});
        this.prevLink = new Element('a', {'class': 'previous', title: 'previous page'});
        this.nextLink = new Element('a', {'class': 'next', title: 'next page'});
        this.element.adopt(this.header, this.menuButton, this.body, new Element('div', {'class': 'clearfix'}));
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
                if(Browser.Features.Touch){
                    this.toggleAnnotationMode();
                }
                this.annotationEditor.show(annotation, annotationElement);
            }
        }).bind(this));
        
        this.annotationEditor = new ecs.pdfviewer.AnnotationEditor(this);
        this.searchPopup = new ecs.pdfviewer.SearchPopup(this);
        this.gotoPagePopup = new ecs.pdfviewer.GotoPagePopup(this);
        this.menuPopup = new ecs.pdfviewer.MenuPopup(this);
        this.annotationSharingPopup = new ecs.pdfviewer.AnnotationSharingPopup(this);
        
        [this.annotationEditor, this.searchPopup, this.gotoPagePopup, this.menuPopup, this.annotationSharingPopup].each(function(popup){
            popup.addEvent('show', (function(){
                this.keyboardNavigationEnabled = false;
                this.gestureNavigationEnabled = false;
                this.currentPopup = popup;
            }).bind(this));
            popup.addEvent('hide', (function(){
                this.keyboardNavigationEnabled = true;
                this.gestureNavigationEnabled = true;
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
        if(Browser.Features.Touch){
            return false;
        }
        this.scrollFx.toTop();
        return true;
    },
    scrollToBottom: function(){
        if(Browser.Features.Touch){
            return false;
        }
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
    update: function(options){
        this.getController().render(this, this.currentPageIndex, options);
    },
    setControllerIndex: function(index){
        this.currentControllerIndex = index;
        this.update();
    },
    cycleController: function(delta){
        index = (this.controllers.length + this.currentControllerIndex + (delta || 1)) % this.controllers.length
        this.setControllerIndex(index);
    },
    setPage: function(pageIndex, update, options){
        if(pageIndex < 0 || pageIndex >= this.pageCount){
            return false;
        }
        if(pageIndex != this.currentPageIndex){
            this.currentPageIndex = pageIndex;
            if(update !== false){
                this.update(options);
            }
            return true;
        }
        return false;
    },
    nextPage: function(delta){
        if(this.setPage(Math.min(this.currentPageIndex + (delta || this.getController().sliceLength), this.pageCount - 1), true, {animationOffset: +1, dontScroll: true})){
            this.scrollToTop();
        }
        return true;
    },
    previousPage: function(delta){
        if(this.setPage(Math.max(this.currentPageIndex - (delta || this.getController().sliceLength), 0), true, {animationOffset: -1, dontScroll: true})){
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
            this.update({animationOffset: delta > 0 ? +1 : -1});
        }
        else{
            this.currentScreen.getElement('.page.current').removeClass('current');
            var el = this.currentScreen.getElement('.page' + this.currentPageIndex);
            el.addClass('current');
            if(!Browser.Features.Touch){
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
        annotation.pageIndex = pageIndex;
        var list = this.annotations[key];
        if(!list){
            list = this.annotations[key] = [];
        }
        var inserted = false;
        for(var i=0;i<list.length;i++){
            if(list[i].y > annotation.y){
                list.splice(i, 0, annotation);
                inserted = true;
                break;
            }
        }
        if(!inserted){
            list.push(annotation);
        }
    },
    getAdjacentAnnotation: function(annotation, d){
        var list = this.annotations['_' + annotation.pageIndex];
        var index = list.indexOf(annotation) + d;
        if(index < list.length && index >= 0){
            return list[index];
        }
        for(var p = annotation.pageIndex + d; p < this.pageCount && p >= 0; p+=d){
            var list = this.annotations['_' + p];
            if(list && list.length){
                return d > 0 ? list[0] : list[list.length - 1];
            }
        }
        return null;
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
        this.renderedAnnotations.push(annotationElement);
        return annotationElement;
    },
    getAnnotationElement: function(annotation){
        for(var i=0;i<this.renderedAnnotations.length;i++){
            var el = this.renderedAnnotations[i];
            if(el.retrieve('annotation') === annotation){
                return el;
            }
        }
        return null;
    },
    gotoAnnotation: function(annotation){
        this.setPage(annotation.pageIndex);
        var el = this.getAnnotationElement(annotation);
        this.annotationEditor.show(annotation, el);
        return true;
    },
    render: function(imageSetKey, offset, w, h, options){
        if(Array.prototype.every.call(arguments, function(val, i){ return val == this.currentRenderArgs[i]}, this)){
            return;
        }
        this.currentRenderArgs = Array.clone(arguments);
        this.renderedAnnotations = [];
        window.location.hash = this.currentPageIndex + 1;
        //this.header.innerHTML = this.title + ' <span class="location">Seite ' + (offset + 1) + (w*h > 1 ? '–' + (offset + w*h) : '') + ' von ' + this.pageCount + '</span>';
        var imageSet = this.imageSets[imageSetKey];
        options = options || {};
        animationOffset = options.animationOffset || 0;
        if(!animationOffset && this.currentScreen){
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
                pageEl.grab(new Element('div', {'class': 'info', html: 'Seite ' + (pageIndex + 1) + ' von ' + this.pageCount}));
                row.grab(pageEl);
            }
            screen.grab(row);
        }
        var screenX = (this.viewportOffset + animationOffset) * 800;
        screen.setStyle('left', screenX + 'px');
        this.innerViewport.grab(screen);

        if(animationOffset){
            var viewportFx = new Fx.Tween(this.innerViewport, {
                property: 'left',
                duration: 600,
                fps: 10,
                transition: Fx.Transitions.linear,
                onComplete: (function(){
                    this.viewportOffset += animationOffset;
                    if(this.currentScreen){
                        this.currentScreen.dispose();
                    }
                    this.currentScreen = screen;
                    if(!Browser.Features.Touch && !options.dontScroll){
                        this.scrollFx.toElement(currentPageElement);
                    }
                    this.viewportAnimated = false;
                }).bind(this)
            });
            this.viewportAnimated = true;
            viewportFx.start(-this.viewportOffset * 800, -screenX);
        }
        else{
            this.currentScreen = screen;
            if(!Browser.Features.Touch && !options.dontScroll){
                this.scrollFx.toElement(currentPageElement);
            }
        }
        // simple preloading
        imageSet.renderPage(offset - 1);
        imageSet.renderPage(offset + w*h);
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
    showHelp: function(){
        var win = window.open(this.helpURL, 'ecshelp');
        win.focus();
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
        popup.show();
        return true;
    },
    showSearch: function(){
        return this.showPopup(this.searchPopup);
    },
    showGotoPage: function(){
        return this.showPopup(this.gotoPagePopup);
    },
    shareAnnotations: function(){
        this.showPopup(this.annotationSharingPopup);
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
        if(!this.keyboardNavigationEnabled || this.viewportAnimated){
            return true;
        }
        var metaKey = !this.metaKey || e[this.metaKey];
        var U = ecs.pdfviewer.utils;
        var atTop = U.isAtTop();
        var atBottom = U.isAtBottom();
        
        for(var i=0;i<this.shortcuts.length;i++){
            var s = this.shortcuts[i];
            if(s.gesture){
                continue;
            }
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
        if(this.annotationMode || this.viewportAnimated){
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
    handleGesture: function(e, type, prop){
        if(!this.gestureNavigationEnabled){
            return;
        }
        for(var i=0;i<this.gestures.length;i++){
            var g = this.gestures[i];
            if(this.annotationMode && !g.annotationMode){
                continue;
            }
            if(g.gesture == type && (!prop || e[prop] == g[prop])){
                if(this[g.command]()){
                    return false;
                }
            }
        }
    },
    handleSwipe: function(e){
        return this.handleGesture(e, 'swipe', 'direction');
    },
    handleTouchhold: function(e){
        return this.handleGesture(e, 'touchhold');
    },
    handlePinch: function(e){
        return this.handleGesture(e, 'pinch');
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
