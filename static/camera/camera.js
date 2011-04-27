var camera = {
    appletURL: '/static/camera/camera.jar',
    format: 'png',

    install: function(){
        this.applet = new Element('applet', {code: 'Camera.class', archive: this.appletURL, width: 0, height: 0});
        // we have to set <param name="initial_focus" value="false"/> to prevent firefox on windows from stealing the keyboard focus (see bug #470):
        this.applet.appendChild(new Element('param', {name: 'initial_focus', value: 'false'}));
        document.body.appendChild(this.applet);
    },
    shoot: function(callback){
        var b64data = this.applet.getBase64Screenshot(this.format);
        var image = new Image();
        image.onload = function(){
            callback(image);
        };
        image.src = "data:image/" + this.format + ";base64," + b64data;
        return image;
    }
};

camera.Camera = new Class({
    Implements: Options,
    options: {
        format: 'png',
        url: '/bugshot/',
        backgroundColor: '#222222',
        title: '',
        form: '',
        canvasSize: {
            width: 800,
            height: 400
        },
        keyTrigger: function(e){
            return false;
        },
        onShow: $empty
    },
    initialize: function(options){
        this.setOptions(options);
        this.disabled = false;
        $(window).addEvent('keypress', (function(e){
            if(this.disabled){
                return;
            }
            if(this.options.keyTrigger(e)){
                this.disabled = true;
                camera.shoot(this.onImageLoaded.bind(this));
            }
        }).bind(this));
        this.install();
    },
    install: function(){
        this.selection = null;
        this.image = null;
        this.zoomStack = [];
        var self = this;

        this.overlay = new Element('div', {
            'class': 'bugshot'
        });
        this.overlay.grab(new Element('div', {
            html: '<h1>' + this.options.title + '</h1><span class="hint">zoom in with drag&amp;drop - zoom out with ctrl+up</span>', 
            'class': 'head'
        }));

        this.form = new Element('form', {
            html: this.options.form,
        });
        this.overlay.grab(this.form);
        
        var submitLink = new Element('a', {html: 'Submit'});
        var cancelLink = new Element('a', {html: 'Cancel'});
        cancelLink.addEvent('click', function(){
            self.cancel();
        });
        submitLink.addEvent('click', function(){
            self.submit();
        });
        this.form.grab(submitLink);
        this.form.grab(cancelLink);

        this.canvas = new Element('canvas', {width: this.options.canvasSize.width, height: this.options.canvasSize.height});
        this.canvas.addEvent('mousedown', function(e){
            var baseCoords = self.canvas.getCoordinates();
            self.selection = {
                x0: e.client.x - baseCoords.left, 
                y0: e.client.y - baseCoords.top, 
                x1: 1, y1: 1
            };
            var mouseMoveListener = function(e){
                self.selection.x1 = e.client.x - baseCoords.left;
                self.selection.y1 = e.client.y - baseCoords.top;
                self.repaintCanvas();
            };
            var mouseUpListener = function(){
                document.body.removeEvent('mousemove', mouseMoveListener);
                document.body.removeEvent('mouseup', mouseUpListener);
                var z = self.zoomStack.getLast(), s = self.selection;
                self.pushZoom({
                    w: Math.abs(s.x1 - s.x0) / z.f,
                    h: Math.abs(s.y1 - s.y0) / z.f,
                    x: z.x + Math.min(s.x0, s.x1) / z.f,
                    y: z.y + Math.min(s.y0, s.y1) / z.f
                });
                self.selection = null;
                self.repaintCanvas();
            };
            document.body.addEvent('mousemove', mouseMoveListener);
            document.body.addEvent('mouseup', mouseUpListener);
            self.repaintCanvas();
        });
        this.overlay.grab(this.canvas);
        
        document.body.appendChild(this.overlay);
    },
    pushZoom: function(z){
        z.f = Math.min(this.canvas.width / z.w, this.canvas.height / z.h);
        if(z.x < 0){
            z.w += z.x;
            z.x = 0;
        }
        if(z.y < 0){
            z.h += z.y;
            z.y = 0;
        }
        this.zoomStack.push(z);
    },
    popZoom: function(){
        if(this.zoomStack.length <= 1){
            return;
        }
        this.zoomStack.pop();
        this.repaintCanvas();
    },
    show: function(){
        this.options.onShow(this);
        this.overlay.show();
        window.addEvent('keypress', (function(e){
            if((e.control || e.meta) && e.key == 'up'){
                this.popZoom();
            }
        }).bind(this));
    },
    cancel: function(){
        this.overlay.hide();
        this.disabled = false;
        this.image = null;
        this.selection = null;
        this.zoomStack = [];
    },
    submit: function(){
        var data = this.form.toQueryString() + '&image=' + encodeURIComponent(this.getDataURL()) + '&url=' + encodeURIComponent(window.location.href);
        var request = new Request({
            url: this.options.url,
            data: data,
            onSuccess: (function(){
                this.cancel();
            }).bind(this),
            onFailure: (function(){
            	alert("Send failure, check for valid input");
            }).bind(this)
        });
        request.send();
    },
    onImageLoaded: function(image){
        this.image = image;
        this.show();
        this.pushZoom({x: 0, y: 0, w: this.image.width, h: this.image.height});
        this.repaintCanvas();
    },
    getDataURL: function(){
        var z = this.zoomStack.getLast();
        var canvas = new Element('canvas', {width: z.w, height: z.h});
        var ctx = canvas.getContext('2d');
        ctx.drawImage(this.image, z.x, z.y, z.w, z.h, 0, 0, z.w, z.h);
        return canvas.toDataURL("image/" + this.options.format);
    },
    repaintCanvas: function(){
        var ctx = this.canvas.getContext("2d");
        ctx.fillStyle = this.options.backgroundColor;
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        if(!this.image){
            return;
        }
        ctx.mozImageSmoothingEnabled = true;
        var z = this.zoomStack.getLast();
        var cw = this.canvas.width, ch = this.canvas.height, t;
        ctx.drawImage(this.image, z.x, z.y, z.w, z.h, 0, 0, z.w * z.f, z.h * z.f);
        
        if(this.selection){
            
            var x0 = this.selection.x0, x1 = this.selection.x1;
            var y0 = this.selection.y0, y1 = this.selection.y1;
            if(x0 > x1){
                t = x0;
                x0 = x1;
                x1 = t;
            }
            if(y0 > y1){
                t = y0;
                y0 = y1;
                y1 = t;
            }
            ctx.fillStyle = "rgba(100, 0, 0, 0.5)";
            ctx.fillRect(0, 0, x0, ch);
            ctx.fillRect(x1, 0, cw - x1, ch);
            ctx.fillRect(x0, 0, x1 - x0, y0);
            ctx.fillRect(x0, y1, x1 - x0, ch - y1);
            ctx.strokeStyle = "#000000";
            ctx.strokeRect(x0, y0, x1 - x0, y1 - y0);
        }            

    }
});
