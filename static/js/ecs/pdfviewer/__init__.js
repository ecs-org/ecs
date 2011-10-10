ecs = window.ecs = window.ecs || {};
ecs.pdfviewer = {};

/* TODO: optimize loading time / responsiveness
 - Guess which images might be accessed next and preload them in the background.
   At least firefox has a default connection limit per server of 15.
 - Reuse page <div>s
 - Optional: use larger sprites
 */

ecs.pdfviewer.utils = {
    PAGE_UP: 33,
    PAGE_DOWN: 34,
    isAtBottom: function(){
        var win = $(window);
        // we have to use <= 1, because firefox somehow manages to scroll one pixel beyond the window or leaves a single pixel unreachable.
        return win.getScrollHeight() - win.getScroll().y - win.getHeight() <= 1;
    },
    isAtTop: function(){
        return $(window).getScroll().y < 3;
    }
};

