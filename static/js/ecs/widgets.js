ecs.Widget = function(el, options) {
    options = options || {};
    this.element = $(el);
    this.element.addClass('ecs-Widget');
    this.element.data('widget', this);
    this.reload_interval = options.reload_interval;
    this.url = options.url;

    var self = this;
    this.element.on('submit', 'form.open-in-widget', function(ev) {
        ev.preventDefault();
        self.load(null, $(this));
    });

    this.element.on('click', 'a.open-in-widget', function(ev) {
        ev.preventDefault();
        var href = $(this).attr('href');
        self.load(href);
    });

    this.element.on('click', 'a.submit-in-widget', function(ev) {
        ev.preventDefault();
        $(this).parents('form.open-in-widget').submit();
    });

    if (this.url)
        this.load();
};
ecs.Widget.prototype = {
    load: function(url, form) {
        if (this.request)
            this.request.abort();

        if (this.url && url && url.indexOf('$CURRENT_URL$') >= 0) {
            url = url.replace(/\$CURRENT_URL\$/,
                encodeURIComponent(this.url.replace(/^https?:\/\/[^/]+/, '')));
        } else if (url) {
            this.url = url;
        }

        var data = form ? new FormData(form[0]) : '';
        this.request = $.ajax({
            url: url || (form ? form.attr('action') : this.url),
            method: form ? form.attr('method') : 'get',
            data: data,
            processData: false,
            contentType: false,
            context: this,
            success: function(data) {
                this.element.html(data);
                this.element.scrollTop(0);
            },
            complete: function(data) {
                if (this.reload_interval) {
                    setTimeout((function(){
                        this.load();
                    }).bind(this), this.reload_interval);
                }
            }
        });
    }
};

ecs.popup = function(options) {
    var modal = $([
        '<div class="modal">',
        '    <div class="modal-dialog">',
        '        <div class="modal-content">',
        '        </div>',
        '    </div>',
        '</div>'
    ].join('\n'));
    $(document.body).append(modal);
    modal = $(modal.get(0));
    modal.modal(options);
    modal.on('hidden.bs.modal', function() {
        modal.remove();
    });
    return modal;
};

ecs.confirm = function(options) {
    var modal = ecs.popup();

    modal.find('.modal-content').html([
        '<div class="modal-body"><p></p></div>',
        '<div class="modal-footer">',
        '    <button type="button" class="btn btn-sm btn-secondary" data-dismiss="modal"></button>',
        '    <button type="button" class="btn btn-sm btn-primary"></button>',
        '</div>'
    ].join('\n'));

    modal.find('.modal-dialog').addClass('modal-sm');
    modal.find('.modal-body p').text(options.question);
    modal.find('button:first').text(options.cancel || 'Cancel');
    modal.find('button:last').text(options.ok || 'OK');
    modal.find('button:last').click(function(ev) {
        ev.preventDefault();
        modal.modal('hide');
        options.success();
    });
};
