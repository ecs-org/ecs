ecs.pdfviewer = {
    /* TODO: optimize loading time / responsiveness
     - Guess which images might be accessed next and preload them in the background.
       At least firefox has a default connection limit per server of 15.
     - Reuse page <div>s
     - Optional: use larger sprites
     */
    ImageSet: new Class({
        initialize: function(options){
            this.sprite = options.sprite;
            this.width = options.width;
            this.height = options.height;
            this.images = [];
        },
        addImage: function(image){
            if(!this.height){
                this.height = image.height;
                this.width = image.width;
            }
            this.images.push(image);
        },
        loadImage: function(image, callback){
            var img = new Image();
            img.addEvent('load', function(){
                if(callback){
                    callback();
                }
            });
            img.src = image.url;
        },
        getSpriteOffset: function(x, y){
            return '-' + parseInt(x * this.getPageWidth()) + 'px -' + parseInt(y * this.getPageHeight()) + 'px';
        },
        getPageWidth: function(){
            return this.width / this.sprite.x;
        },
        getPageHeight: function(){
            return this.height / this.sprite.y;
        },
        renderPage: function(pageIndex){
            var el = new Element('div', {'class': 'loading'});
            var perImage = this.sprite.x * this.sprite.y;
            var imageIndex = parseInt(pageIndex / perImage);
            var spriteIndex = pageIndex % perImage;
            var spriteX = spriteIndex % this.sprite.x;
            var spriteY = parseInt(spriteIndex / this.sprite.x);
            var image = this.images[imageIndex];
            el.setStyles({
                'width': this.getPageWidth() + 'px',
                'height': this.getPageHeight() + 'px'
            });
            var offset = this.getSpriteOffset(spriteX, spriteY);
            this.loadImage(image, function(){
                el.removeClass('loading');
                el.setStyles({
                    'background-image': 'url(' + image.url + ')',
                    'background-position': offset
                });
            });
            return el;
        }
    }),
    
    utils: {
        isAtBottom: function(){
            var win = $(window);
            // we have to use <= 0, because firefox somehow manages to scroll one pixel beyond the window.
            return win.getScrollHeight() - win.getScroll().y - win.getHeight() <= 0;
        },
        isAtTop: function(){
            return $(window).getScroll().y == 0
        }
    },

    DocumentViewer: new Class({
        initialize: function(el, options){
            this.element = $(el);
            this.pageCount = options.pageCount;
            this.controllers = options.controllers;
            this.wheelThreshold = options.wheelThreshold || 20.0;
            this.title = options.title;
            this.searchURL = options.searchURL;
            this.metaKey = options.metaKey || '';

            this.imageSets = {};
            this.currentPageIndex = 0;
            this.currentControllerIndex = 0;
            this.currentScreen = null;
            this.currentContent = [];

            this._wheelCounter = 0;
            this._wheelTimeout = null;
            this._wheelReset = (function(){this._wheelCounter = 0; this._wheelTimeout = null;}).bind(this);
            $(window).addEvent('click', this.handleClick.bind(this));
            $(window).addEvent('mousewheel', this.handleMouseWheel.bind(this));
            
            this.body = new Element('div', {'class': 'body'});
            this.viewport = new Element('div', {'class': 'viewport'});
            this.header = new Element('div', {'class': 'header', html: this.title});
            this.prevLink = new Element('a', {'class': 'previous', html: '<b>previous</b>'});
            this.nextLink = new Element('a', {'class': 'next', html: '<b>next</b>'});
            this.element.grab(this.header);
            this.element.grab(this.body);
            this.body.grab(this.prevLink);
            this.body.grab(this.viewport);
            this.body.grab(this.nextLink);
            this.prevLink.addEvent('click', (function(){
                this.previousPage();
            }).bind(this));
            this.nextLink.addEvent('click', (function(){
                this.nextPage();
            }).bind(this));
        },
        gotoAnchor: function(hash){
            hash = hash || window.location.hash;
            if(hash){
                this.setPage(parseInt(hash.substring(1)) - 1, false);
                this.setControllerIndex(this.controllers.length - 1);
            }
        },
        setMetaKey: function(meta){
            this.metaKey = meta;
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
            if(pageIndex != this.currentPageIndex){
                this.currentPageIndex = pageIndex;
                if(update !== false){
                    this.update();
                }
            }
        },
        nextPage: function(delta){
            $(document.body).scrollTo(0, 0);
            this.setPage(Math.min(this.currentPageIndex + (delta || this.getController().sliceLength), this.pageCount - 1));
        },
        previousPage: function(delta){
            this.setPage(Math.max(this.currentPageIndex - (delta || this.getController().sliceLength), 0));
        },
        render: function(imageSetKey, offset, w, h){
            if($A(arguments).every((function(val, index){ return this.currentContent[index] == val;}).bind(this))){
                return;
            }
            window.location.hash = this.currentPageIndex + 1;
            this.header.innerHTML = this.title + ' Page ' + (offset + 1) + (w*h > 1 ? ' - ' + (offset + w*h) : '') + ' von ' + this.pageCount;
            this.currentContent = $A(arguments);
            var imageSet = this.imageSets[imageSetKey];
            if(this.currentScreen){
                this.currentScreen.dispose();
            }
            var screen = new Element('div', {'class': 'screen'});
            for(var y = 0; y < h; y++){
                var row = new Element('div', {'class': 'row'});
                for(var x = 0; x < w; x++){
                    var pageIndex = offset + y*w + x;
                    if(pageIndex >= this.pageCount){
                        break;
                    }
                    var pageEl = imageSet.renderPage(pageIndex);
                    pageEl.addClass('page');
                    pageEl.id = 'p' + imageSetKey + '_' + pageIndex;
                    if(pageIndex == this.currentPageIndex){
                        pageEl.addClass('current');
                    }
                    pageEl.grab(new Element('div', {'class': 'info', html: 'Seite ' + (pageIndex + 1)}));
                    row.grab(pageEl);
                }
                screen.grab(row);
            }
            this.viewport.grab(screen);
            this.currentScreen = screen;
            return screen;
        },
        handleKeyPress: function(e){
            var metaKey = !this.metaKey || e[this.metaKey];
            var U = ecs.pdfviewer.utils;
            var atTop = U.isAtTop();
            var atBottom = U.isAtBottom();
            if(e.key == 's'){
                var searchDialog = new ecs.Dialog(this.searchURL, {
                    size: {
                        width: 500,
                        height: 400
                    },
                    onClose: (function(){
                        this.key_nav_enabled = true;
                    }).bind(this)
                });
                return false;
            }
            else if(e.key == 'enter'){
                this.cycleController(+1);
                return false;
            }
            else if(e.key == 'up'){
                if(metaKey){
                    this.cycleController(-1);
                }
                else if(atTop){
                    this.previousPage(this.getController().sliceLength);
                }
                return false;
            }
            else if(e.key == 'down'){
                if(metaKey){
                    this.cycleController(+1);
                }
                else if(atBottom){
                    this.nextPage();
                }
                return false;
            }
            else if(metaKey && e.key == 'right'){
                if(e.shift){
                    this.setPage(this.pageCount - 1);
                }
                else{
                    this.nextPage();
                }
                return false;
            }
            else if(metaKey && e.key == 'left'){
                if(e.shift){
                    this.setPage(0);
                }
                else{
                    this.previousPage();
                }
                return false;
            }
            else if(e.key == 'a' && this.getController().options.showAnnotations){
                var hint = new Element('div', {'class': 'annotationHint', 'html': 'Annotation Mode<br/>Drag &amp; Drop or ESC to Quit'});
                $(document.body).grab(hint);
                
                return false;
            }
        },
        handleMouseWheel: function(e){
            var U = ecs.pdfviewer.utils;
            if(e.wheel > 0 && U.isAtTop() || e.wheel < 0  && U.isAtBottom()){
                if(this._wheelTimeout){
                    clearTimeout(this._wheelTimeout)
                }
                else{
                    this._wheelTimeout = setTimeout(this._wheelReset, 100);
                }
                this._wheelCounter += Math.abs(e.wheel);
                if(this._wheelCounter >= this.wheelThreshold){
                    this._wheelCounter = 0;
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
            if(e.alt){
                this.cycleController(e.shift ? -1 : +1);
            }
            else if(target.hasClass('page')){
                var pageIndex = parseInt(target.id.split('_').getLast());
                this.setPage(pageIndex, false);
                this.setControllerIndex(this.controllers.length - 1);
            }
        }
    }),

    Controller: new Class({
        initialize: function(imageSet, x, y, options){
            this.imageSet = imageSet;
            this.x = x;
            this.y = y;
            this.sliceLength = x * y;
            this.options = options || {'showAnnotations': true};
        },
        render: function(viewer, pageIndex){
            var blockIndex = parseInt(Math.floor(pageIndex / this.sliceLength));
            viewer.render(this.imageSet, blockIndex * this.sliceLength, this.x, this.y);
        }
    }),
    
    Annotation: new Class({
        initialize: function(){
            
        }
    })
};
