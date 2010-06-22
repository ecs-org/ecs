ecs.Tab = new Class({
    Implements: Events,
    initialize: function(controller, header, panel, index){
        this.controller = controller;
        this.header = header;
        this.panel = panel;
        this.index = index;
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
        this.setClass(this.controller.options.selectedTabClass, selected);
        this.panel.setStyle('display', selected ? 'block' : 'none');
        this.selected = selected;
        this.fireEvent('select');
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

ecs.TabController = new Class({
    Implements: [Options, Events],
    options: {
        tabIdPrefix: 'tab-',
        selectedTabClass: 'active'
    },
    initialize: function(headerContainer, options){
        this.setOptions(options);
        this.tabs = [];
        this.selectedTab = null;
        this.headerContainer = headerContainer;
        var index = 0;
        var initialSelection = null;
        headerContainer.getChildren('li').each(function(header){
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
        }, this);
        this.selectTab(initialSelection || this.tabs[0], true);
    },
    onTabHeaderClick: function(event, tab){
        this.selectTab(tab);
    },
    selectTab: function(tab, initial){
        if(tab == this.selectedTab){
            return;
        }
        if(this.selectedTab){
            this.selectedTab.setSelected(false);
        }
        this.selectedTab = tab;
        if(tab){
            tab.setSelected(true);
        }
        this.fireEvent('tabSelectionChange', tab, !!initial);
    },
    getSelectedTab: function(){
        return this.selectedTab;
    },
    getTabs: function(){
        return this.tabs;
    },
    getPanels: function(){
        return this.tabs.map(function(tab){ return tab.panel;})
    },
    getTabForElement: function(el){
        for(var i=0;i<this.tabs.length;i++){
            var tab = this.tabs[i];
            if(tab.panel == el || tab.panel.hasChild(el)){
                return tab;
            }
        }
        return null;
    },
    getTab: function(index){
        return this.tabs[index];
    },
    addTab: function(header, panel, inject){
        panel.id = panel.id || this.options.tabIdPrefix + this.tabs.length;
        header = new Element('li', {html: '<a href="#' + panel.id + '">' + header + '</a>'});
        this.headerContainer.grab(header);
        if(inject){
            panel.inject(this.tabs.getLast().panel, 'after');
        }
        var tab = new ecs.Tab(this, header, panel, this.tabs.length);
        this.tabs.push(tab);
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
