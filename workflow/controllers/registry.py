
def _fqn(obj):
    return "%s.%s" % (obj.__module__, obj.__name__)


class ControllerRegistry(object):
    def __init__(self):
        self.loaded = False
        self.node_controller_map = {}
        self.guard_map = {}

    def clear_caches(self):
        for c in self.node_controller_map.itervalues():
            del c._meta.node_type
        for key in self.node_controller_map.keys():
            try:
                del self.node_controller_map[int(key)]
            except ValueError:
                pass
        for g in self.guard_map.itervalues():
            del g._meta.instance
            
    def bind_node(self, node, workflow):
        try:
            cls = self.node_controller_map[node.node_type_id]
        except KeyError:
            node_type = node.node_type
            try:
                cls = self.node_controller_map[node_type.implementation]
                self.node_controller_map[node_type.id] = cls
            except KeyError:
                raise KeyError("Missing NodeController for NodeType %s" % node.node_type)
        return cls(node, workflow)
                
    def bind_edge(self, edge, workflow):
        return EdgeController(edge, workflow)
        
    def bind_guard(self, edge, workflow):
        if not edge.guard_id:
            return lambda: True
        try:
            func = self.guard_map[edge.guard_id]
        except KeyError:
            try:
                func = self.guard_map[edge.guard.implementation]
                self.guard_map[edge.guard_id] = func
            except KeyError:
                raise KeyError("Missing guard implementation for %s" % edge.guard)
        return lambda: func(workflow) != edge.negated

    def add_controller(self, controller):
        name = _fqn(controller)
        self.node_controller_map[name] = controller
        return name
        
    def add_guard(self, guard):
        name = _fqn(guard)
        self.guard_map[name] = guard
        return name


_registry = ControllerRegistry()

bind_edge = _registry.bind_edge
bind_node = _registry.bind_node
bind_guard = _registry.bind_guard
add_controller = _registry.add_controller
add_guard = _registry.add_guard
clear_caches = _registry.clear_caches

def iter_guards():
    return _registry.guard_map.itervalues()
    
def iter_activities():
    for c in _registry.node_controller_map.itervalues():
        if hasattr(c, 'perform'):
            yield c
            
def iter_controls():
    for c in _registry.node_controller_map.itervalues():
        if not hasattr(c, 'perform'):
            yield c
