ecs = window.ecs = window.ecs || {};
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
        this.touchStartListener = this.onTouchStart.bind(this);
        this.touchEndListener = this.onTouchEnd.bind(this);
        this.touchMoveListener = this.onTouchMove.bind(this);
        this.start = null;
        this.basePosition = null;
        this.point = null;
        this.frameOverlay = new Element('div', {'class': 'ecs-DragDropFrameOverlay'});
        this.attach();
        this.touchmoveLog = [];
    },
    attach: function(){
        if(Browser.Features.Touch){
            this.element.addEvent('touchstart', this.touchStartListener);
            this.element.addEvent('touchmove', this.touchMoveListener);
            this.element.addEvent('touchend', this.touchEndListener);
        }
        else{
            this.element.addEvent('mousedown', this.mouseDownListener);
            this.element.addEvent('mouseup', this.mouseUpListener);
            this.element.addEvent('mousemove', this.mouseMoveListener);
        }
    },
    detach: function(){
        if(Browser.Features.Touch){
            this.element.removeEvent('touchstart', this.touchStartListener);
            this.element.removeEvent('touchmove', this.touchMoveListener);
            this.element.removeEvent('touchend', this.touchEndListener);
        }
        else{
            this.element.removeEvent('mousedown', this.mouseDownListener);
            this.element.removeEvent('mouseup', this.mouseUpListener);
            this.element.removeEvent('mousemove', this.mouseMoveListener);
        }
    },
    _touchPoint: function(e){
        return {
            x: e.changedTouches[0].clientX, 
            y: e.changedTouches[0].clientY, 
        };
    },
    onStart: function(pos){
        this.basePosition = this.element.getPosition();
        this.start = pos;
        this.element.grab(this.frameOverlay);
        this.onMove(pos);
    },
    onMove: function(pos){
        if(!this.start){
            return;
        }
        this.point = pos;
        if(this.paintOverlay){
            this.paintFrame();
        }
    },
    onEnd: function(pos){
        var frame = this.getFrame();
        this.start = null;
        this.frameOverlay.dispose();
        this.fireEvent('complete', frame);
    },
    onTouchStart: function(e){
        this.onStart(this._touchPoint(e));
    },
    onTouchMove: function(e){
        this.onMove(this._touchPoint(e));
    },
    onTouchEnd: function(e){
        this.onEnd(this._touchPoint(e));
    },
    onMouseDown: function(e){
        this.onStart(e.page);
    },
    onMouseUp: function(e){
        this.onEnd(e.page);
    },
    onMouseMove: function(e){
        this.onMove(e.page);
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
