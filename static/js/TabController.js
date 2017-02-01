ecs.Tab = function(controller, header) {
    this.controller = controller;
    this.header = header;
    this.panel = $(header.attr('href'));
    this.group = null;  /* set by ecs.TabGroup */
};
ecs.Tab.prototype = {
    toggleClass: function(cls, set) {
        this.header.toggleClass(cls, set);
        this.panel.toggleClass(cls, set);
    },
    setErrorState: function() {
        this.header.addClass('text-danger');
        this.panel.addClass('errors');
    },
    setSelected: function(selected) {
        this.toggleClass('active', selected);
        this.panel.toggleClass('show', selected);
        this.group.selectedTab = this;

        if (selected) {
            var title = document.title.split(' | ');
            title[0] = this.header.html();
            document.title = title.join(' | ');

            this.panel.find('textarea').each(function() {
                var textarea = $(this).data('textarea');
                if (textarea)
                    textarea.updateHeight();
            });
        }
    },
    setDisabled: function(disabled) {
        this.toggleClass('disabled', disabled);
        this.panel.find('input, select, textarea').attr('disabled', disabled);
    }
};

ecs.TabGroup = function(controller, header, container, tabs) {
    this.controller = controller;
    this.header = header;
    this.container = container;
    this.tabs = tabs;
    this.selectedTab = tabs[0];
    for (var i = 0; i < tabs.length; i++)
        tabs[i].group = this;

    this.header.click((function(ev) {
        ev.preventDefault();
        controller.selectTabGroup(this);
    }).bind(this));
};
ecs.TabGroup.prototype = {
    setSelected: function(selected) {
        this.header.toggleClass('active', selected);
        this.container.toggleClass('show', selected);
        if (selected && this.selectedTab)
            window.location.hash = this.selectedTab.header.attr('href');
    }
};

ecs.TabController = function(tabGroupContainers) {
    this.tabs = [];
    this.tabGroups = [];
    this.selectedTab = null;
    this.selectedTabGroup = null;

    var initialSelection = null;
    $(tabGroupContainers).each($.proxy(function(controller) {
        var header = $(this);
        var container = $(header.attr('href'));
        var tabs = [];
        container.find('a.nav-link').each(function() {
            var link = $(this);
            var tab = new ecs.Tab(controller, link);
            if (window.location.hash == link.attr('href'))
                initialSelection = tab;
            if (!initialSelection && link.hasClass('active'))
                initialSelection = tab;
            link.removeClass('active');
            controller.tabs.push(tab);
            tabs.push(tab);
        });
        controller.tabGroups.push(new ecs.TabGroup(controller, header, container, tabs));
    }, null, this));
    this.selectTab(initialSelection || this.tabs[0]);
    if (window.location.hash)
        $(window).scrollTop(0);

    $(window).on('hashchange', this.onHashChange.bind(this));
};
ecs.TabController.prototype = {
    onHashChange: function(ev) {
        var new_hash = window.location.hash;
        var tab = new_hash ? this.getTab(new_hash) : this.tabs[0];
        if (tab) {
            ev.preventDefault();
            this.selectTab(tab);
        }
    },
    selectTab: function(tab) {
        if (tab === this.selectedTab)
            return;

        if (this.selectedTab)
            this.selectedTab.setSelected(false);

        this.selectedTab = tab;
        if (tab) {
            tab.setSelected(true);
            this.selectTabGroup(tab.group);
        }
    },
    selectTabGroup: function(tabGroup) {
        if (tabGroup === this.selectedTabGroup)
            return;

        if (this.selectedTabGroup)
            this.selectedTabGroup.setSelected(false);

        this.selectedTabGroup = tabGroup;
        if (tabGroup)
            tabGroup.setSelected(true);
    },
    getTab: function(href) {
        for (var i = 0; i < this.tabs.length; i++) {
            var tab = this.tabs[i];
            if (tab.header.attr('href') == href)
                return tab;
        }
    }
};
