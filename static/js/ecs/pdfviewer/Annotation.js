ecs.pdfviewer.Annotation = new Class({
    initialize: function(pk, text, x, y, w, h, author){
        this.pk = pk;
        this.text = text;
        this.x = x;
        this.y = y;
        this.w = w;
        this.h = h;
        this.author = author;
    },
    attachTo: function(el, onShow){
        var a = new Element('div', {'class': 'annotation'});
        var dim = el.getSize();
        a.setStyle('top', (this.y * dim.y) + 'px');
        a.setClass('foreign', !!this.author);
        var overlay = new Element('div', {'class': 'overlay'});
    
        overlay.setStyles({
            left: (this.x * dim.x) + 'px', 
            top: '0px',
            width: (this.w * dim.x) + 'px',
            height: (this.h * dim.y) + 'px'
        });
        a.grab(overlay);
        var marker = new Element('div', {'class': 'marker'});
        a.grab(marker);
        el.grab(a);
        if(onShow){
            marker.addEvent('click', onShow);
            overlay.addEvent('dblclick', onShow);
        }
        return a;
    },
    startAnnotationMode: function(annotationElement){
        var overlay = annotationElement.getFirst('.overlay');
        var resizeHandle = new Element('div', {'class': 'resizeHandle'});
        var dragHandle = new Element('div', {'class': 'dragHandle'});
        overlay.grab(dragHandle);
        overlay.grab(resizeHandle);
        overlay.makeResizable({
            handle: resizeHandle,
            onComplete: this.postDragDrop.bind(this)
        });
        new Drag.Move(overlay, {
            handle: dragHandle,
            onComplete: this.postDragDrop.bind(this)
        });
    },
    endAnnotationMode: function(annotationElement){
        var overlay = annotationElement.getFirst('.overlay');
        overlay.getFirst('.resizeHandle').dispose();
        overlay.getFirst('.dragHandle').dispose();
    },
    postDragDrop: function(overlay){
        var annotationElement = overlay.getParent('.annotation');
        var pageEl = annotationElement.getParent('.page');
        var pageSize = pageEl.getSize();
        var bounds = overlay.getStyles('left', 'top', 'width', 'height');
        this.x = parseInt(bounds.left) / pageSize.x;
        this.y += parseInt(bounds.top) / pageSize.y;
        this.w = parseInt(bounds.width) / pageSize.x;
        this.h = parseInt(bounds.height) / pageSize.y;
        annotationElement.setStyle('top', (parseInt(annotationElement.getStyle('top')) + parseInt(bounds.top)) + 'px');
        overlay.setStyle('top', '0px');
        annotationElement.removeClass('foreign');
        this.author = null;
    }
});