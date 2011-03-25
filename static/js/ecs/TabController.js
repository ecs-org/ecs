ecs.Tab = new Class({
    Implements: Events,
    initialize: function(controller, header, panel, index){
        this.controller = controller;
        this.header = header;
        this.panel = panel;
        this.index = index;
        this.group = null;
        this.panel.setStyle('display', 'none');
        this.clickHandler = controller.onTabHeaderClick.bindWithEvent(controller, this);
        this.header.addEvent('click', this.clickHandler);
        this.selected = false;
    },
    setClass: function(cls, set){
        this.header.setClass(cls, set);
        this.panel.setClass(cls, set);
    },
    setSelected: function(selected){
        window.location.hash = '#' + this.header.getElement('a').href.split('#')[1];
        this.setClass(this.controller.options.selectedTabClass, selected);
        this.panel.setStyle('display', selected ? 'block' : 'none');
        this.selected = selected;
        this.fireEvent(selected ? 'select' : 'deselect', this);
    },
    setDisabled: function(disabled){
        this.setClass('disabled', disabled);
        ecs.disabledFormFields(this.panel, disabled);
    },
    remove: function(){
        this.header.removeEvent('click', this.clickHandler);
        this.clickHandler = null;
        this.header.dispose();
        this.panel.dispose();
        this.fireEvent('remove');
    },
    getIndex: function(){
        return this.controller.tabs.indexOf(this);
    }
});

ecs.TabGroup = new Class({
    initialize: function(controller, header, container, tabs){
        this.controller = controller;
        this.header = header;
        this.container = container;
        this.tabs = [];
        this.selectedTab = tabs ? tabs[0] : null;
        this.selected = false;
        this.tabSelectionHandler = this.onTabSelect.bind(this);
        this.container.setStyle('display', 'none');
        tabs.each(function(tab){
            this.addTab(tab);
        }, this);
        if(this.header){
            this.header.addEvent('click', controller.onTabGroupHeaderClick.bindWithEvent(controller, this));
        }
    },
    addTab: function(tab){
        this.tabs.push(tab);
        tab.group = this;
        if(this.tabs.length === 1){
            this.selectedTab = tab;
        }
        tab.addEvent('select', this.tabSelectionHandler);
    },
    onTabSelect: function(tab){
        this.selectedTab = tab;
    },
    removeTab: function(tab){
        this.tabs.erase(tab);
        if(tab === this.selectedTab){
            this.selectedTab = this.tabs[0];
        }
        tab.removeEvent('select', this.tabSelectionHandler);
    },
    setHeaderClass: function(cls, set){
        if(this.header){
            this.header.setClass(cls, set);
        }
    },
    setClass: function(cls, set){
        this.setHeaderClass(cls, set);
        this.tabs.each(function(tab){
            tab.setClass(cls, set);
        });
    },
    setSelected: function(selected){
        this.selected = selected;
        if(this.header){
            this.header.setClass(this.controller.options.selectedTabClass, selected);
        }
        this.controller.selectTab(this.selectedTab);
        this.container.setStyle('display', selected ? 'block' : 'none');
    }
});

ecs.TabController = new Class({
    Implements: [Options, Events],
    options: {
        tabIdPrefix: 'tab-',
        selectedTabClass: 'active',
        tabGroupHeaderSelector: 'a',
        tabGroupContainerSelector: 'ul',
        tabGroupSelector: null
    },
    initialize: function(tabGroupContainers, options){
        this.setOptions(options);
        this.tabs = [];
        this.tabGroups = [];
        this.selectedTab = null;
        this.selectedTabGroup = null;
        this.tabGroupContainers = tabGroupContainers;

        var index = 0;
        var initialSelection = null;
        tabGroupContainers.each(function(el){
            var header = el.getFirst(this.options.tabGroupHeaderSelector);
            var container = el.getFirst(this.options.tabGroupContainerSelector);
            var tabs = [];
            container.getElements('li').each(function(header){
                var hash = header.getElement('a').href.split('#')[1];
                var panel = $(hash);
                var tab = new ecs.Tab(this, header, panel, index++);
                if(window.location.hash == '#' + hash){
                    initialSelection = tab;
                }
                if(!initialSelection && header.hasClass(this.options.selectedTabClass)){
                    initialSelection = tab;
                }
                header.removeClass(this.options.selectedTabClass);
                this.tabs.push(tab);
                tabs.push(tab);
            }, this);
            this.tabGroups.push(new ecs.TabGroup(this, header, container, tabs));
        }, this);
        this.selectTab(initialSelection || this.tabs[0], true);
    },
    onTabHeaderClick: function(evt, tab){
        this.selectTab(tab);
        evt.stop();
    },
    onTabGroupHeaderClick: function(evt, tabGroup){
        this.selectTabGroup(tabGroup);
        evt.stop();
    },
    selectTab: function(tab, initial){
        if(tab === this.selectedTab){
            return;
        }
        if(this.selectedTab){
            this.selectedTab.setSelected(false);
        }
        this.selectedTab = tab;
        if(tab){
            tab.setSelected(true);
            this.selectTabGroup(tab.group, initial);
        }
        this.fireEvent('tabSelectionChange', tab, !!initial);
    },
    selectTabGroup: function(tabGroup, initial){
        if(tabGroup === this.selectedTabGroup){
            return;
        }
        if(this.selectedTabGroup){
            this.selectedTabGroup.setSelected(false);
        }
        this.selectedTabGroup = tabGroup;
        if(tabGroup){
            tabGroup.setSelected(true);
        }
        this.fireEvent('tabGroupSelectionChange', tabGroup, !!initial);
    },
    getSelectedTab: function(){
        return this.selectedTab;
    },
    getSelectedTabGroup: function(){
        return this.selectedTabGroup;
    },
    getTabs: function(){
        return this.tabs;
    },
    getPanels: function(){
        return this.tabs.map(function(tab){ return tab.panel;})
    },
    getTabForElement: function(el){
        el = $(el);
        for(var i=0;i<this.tabs.length;i++){
            var tab = this.tabs[i];
            if(tab.panel === el || tab.panel.hasChild(el)){
                return tab;
            }
        }
        return null;
    },
    getTab: function(index){
        return this.tabs[index];
    },
    getTabGroupForElement: function(el){
        el = $(el);
        for(var i=0;i<this.tabGroups.length;i++){
            var tabGroup = this.tabGroups[i];
            if(tabGroup.container === el || tabGroup.container.hasChild(el)){
                return tabGroup;
            }
        }
        return null;
    },
    addTab: function(tabGroup, header, panel, inject){
        panel.id = panel.id || this.options.tabIdPrefix + this.tabs.length;
        header = new Element('li', {html: '<a href="#' + panel.id + '">' + header + '</a>'});
        tabGroup.container.grab(header);
        if(inject){
            panel.inject(this.tabs.getLast().panel, 'after');
        }
        var tab = new ecs.Tab(this, header, panel, this.tabs.length);
        this.tabs.push(tab);
        tabGroup.addTab(tab);
        this.fireEvent('tabAdded', tab);
        return tab;
    },
    removeTab: function(tab){
        this.tabs.erase(tab);
        tab.remove();
        if(tab == this.selectedTab){
            this.selectTab(this.tabs[tab.index - 1]);
        }
        this.fireEvent('tabRemoved', tab);
    }
});
