ecs.dragdrop = {};

function _tlog(msg){
    document.body.appendChild(new Element('div', {html: msg, style: 'color:#fff'}));
}

ecs.dragdrop.Frame = new Class({
    Implements: Events,
    initialize: function(el, options){
        this.element = $(el);
        options = options || {};
        this.paintOverlay = options.paintOverlay || true;
        this.mouseDownListener = this.onMouseDown.bind(this);
        this.mouseUpListener = this.onMouseUp.bind(this);
        this.mouseMoveListener = this.onMouseMove.bind(this);
        this.start = null;
        this.basePosition = null;
        this.point = null;
        this.frameOverlay = new Element('div', {'class': 'ecs-DragDropFrameOverlay'});
        this.attach();
    },
    attach: function(){
        this.element.addEvent('mousedown', this.mouseDownListener);
        this.element.addEvent('mouseup', this.mouseUpListener);
        this.element.addEvent('mousemove', this.mouseMoveListener);
        /*
        document.addListener('touchstart', this.moveDownListener);
        document.addListener('touchend', this.mouseUpListener);
        document.addListener('touchmove', this.mouseMoveListener);
        */
    },
    detach: function(){
        this.element.removeEvent('mousedown', this.mouseDownListener);
        this.element.removeEvent('mouseup', this.mouseUpListener);
        this.element.removeEvent('mousemove', this.mouseMoveListener);
        /*
        document.removeListener('touchstart', this.moveDownListener);
        document.removeListener('touchend', this.mouseUpListener);
        document.removeListener('touchmove', this.mouseMoveListener);
        */
    },
    onMouseDown: function(e){
        //_tlog("down " + e);
        this.basePosition = this.element.getPosition();
        this.start = e.page;
        this.element.grab(this.frameOverlay);
        this.onMouseMove(e);
    },
    onMouseUp: function(e){
        //_tlog("up " + e);
        var frame = this.getFrame();
        this.start = null;
        this.frameOverlay.dispose();
        this.fireEvent('complete', frame);
    },
    getFrame: function(){
        var dx = this.point.x - this.start.x;
        var dy = this.point.y - this.start.y;
        var f = {
            sx: dx < 0 ? -1 : 1, 
            sy: dy < 0 ? -1 : 1,
            w: Math.abs(dx),
            h: Math.abs(dy)
        };
        f.x = Math.min(this.point.x, this.start.x) - this.basePosition.x;
        f.y = Math.min(this.point.y, this.start.y) - this.basePosition.y;
        return f;
    },
    onMouseMove: function(e){
        //_tlog("move " + e + e.event.clientX + "/" + e.event.clientY);
        //e.stop();
        if(!this.start){
            return;
        }
        try{
            this.point = e.page;
            if(this.paintOverlay){
                this.paintFrame();
            }
        }
        catch(e){
            _tlog(e);
        }
        //return false;
    },
    paintFrame: function(x, y, w, h, rx, ry){
        var f = this.getFrame();
        this.frameOverlay.setStyles({
            'left': f.x + 'px',
            'top': f.y + 'px',
            'width': f.w + 'px',
            'height': f.h + 'px'
        })
    }
});
