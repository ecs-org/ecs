ecs.pdfviewer.ImageSet = new Class({
    initialize: function(options){
        this.sprite = options.sprite;
        this.width = options.width;
        this.height = options.height;
        this.images = [];
        this.borderWidths = options.borderWidths;
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
        return '-' + (parseInt(x * this.getPageWidth()) + this.borderWidths.left) + 'px'
            + ' -' + (parseInt(y * this.getPageHeight()) + this.borderWidths.top) + 'px';
    },
    getPageWidth: function(){
        return this.width / this.sprite.x;
    },
    getPageHeight: function(){
        return this.height / this.sprite.y;
    },
    renderPage: function(pageIndex, callback){
        var el = new Element('div', {'class': 'loading'});
        el.store('pageIndex', pageIndex);
        var perImage = this.sprite.x * this.sprite.y;
        var imageIndex = parseInt(pageIndex / perImage);
        var spriteIndex = pageIndex % perImage;
        var spriteX = spriteIndex % this.sprite.x;
        var spriteY = parseInt(spriteIndex / this.sprite.x);
        var image = this.images[imageIndex];
        el.setStyles({
            'width': (this.getPageWidth() - this.borderWidths.left - this.borderWidths.right) + 'px',
            'height': (this.getPageHeight() - this.borderWidths.top - this.borderWidths.bottom) + 'px'
        });
        var offset = this.getSpriteOffset(spriteX, spriteY);
        this.loadImage(image, function(){
            el.removeClass('loading');
            el.setStyles({
                'background-image': 'url(' + image.url + ')',
                'background-position': offset
            });
            if(callback){
                callback(el);
            }
        });
        return el;
    }
});
