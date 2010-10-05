ecs.pdfviewer = {
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
        loadImage: function(url, callback){
            var img = new Image();
            img.addEvent('load', function(){
                if(callback){
                    callback();
                }
            });
            img.src = url;
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
            var url = this.images[imageIndex].url;
            el.setStyles({
                'width': this.getPageWidth() + 'px',
                'height': this.getPageHeight() + 'px'
            });
            var offset = this.getSpriteOffset(spriteX, spriteY);
            this.loadImage(url, function(){
                el.removeClass('loading');
                el.setStyles({
                    'background-image': 'url(' + url + ')',
                    'background-position': offset
                });
            });
            return el;
        }
    }),

    DocumentViewer: new Class({
        initialize: function(el, options){
            this.element = $(el);
            this.pageCount = options.pageCount;
            this.imageSets = {};
            this.controllers = options.controllers;
            this.currentPageIndex = 0;
            this.currentControllerIndex = 0;
            this.currentScreen = null;
            this.currentContent = [];
            $(window).addEvent('click', (function(e){
                this.handleClick(e);
            }).bind(this));
            
            this.title = options.title;
            this.header = new Element('div', {'class': 'header', html: this.title});
            this.element.grab(this.header);
            this.searchURL = options.searchURL;
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
            this.setPage(Math.min(this.currentPageIndex + (delta || 1), this.pageCount - 1));
        },
        previousPage: function(delta){
            this.setPage(Math.max(this.currentPageIndex - (delta || 1), 0));
        },
        render: function(imageSetKey, offset, w, h){
            if($A(arguments).every((function(val, index){ return this.currentContent[index] == val;}).bind(this))){
                return;
            }
            this.header.innerHTML = this.title + ' Seite ' + (offset + 1) + ' - ' + (offset + w*h) + ' von ' + this.pageCount;
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
                    pageEl.grab(new Element('div', {'class': 'info', html: 'Seite ' + pageIndex}));
                    row.grab(pageEl);
                }
                screen.grab(row);
            }
            this.element.grab(screen);
            this.currentScreen = screen;
            return screen;
        },
        handleKeyPress: function(e){
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
            }
            else if(e.alt && e.key == 'up'){
                this.cycleController(-1);
            }
            else if(e.alt && e.key == 'down' || e.key == 'enter'){
                this.cycleController(+1);
            }
            else if(e.alt && e.key == 'right'){
                if(e.shift){
                    this.setPage(this.pageCount - 1);
                }
                else{
                    this.nextPage(this.getController().sliceLength);
                }
            }
            else if(e.alt && e.key == 'left'){
                if(e.shift){
                    this.setPage(0);
                }
                else{
                    this.previousPage(this.getController().sliceLength);
                }
            }
            else if(e.key == 'a'){
                
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
            this.options = options || {};
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
