def workaround_16759():
    """
    see https://code.djangoproject.com/ticket/16759
    this is https://code.djangoproject.com/attachment/ticket/16759/16759_cleaned_up_where_clone.diff
    rewritten as monkey patch and backported to django 1.2.3
    """
    from django.db.models.sql.aggregates import Aggregate
    from django.db.models.sql.where import EverythingNode, NothingNode, ExtraWhere, Constraint
    from django.db.models.sql.query import Query
    from django.utils.tree import Node

    def _immutable_clone(self):
        return self

    from django.db.models.sql.datastructures import Empty
    from copy import deepcopy
    def _Query_clone(self, klass=None, memo=None, **kwargs):
        obj = Empty()
        obj.__class__ = klass or self.__class__
        obj.model = self.model
        obj.alias_refcount = self.alias_refcount.copy()
        obj.alias_map = self.alias_map.copy()
        obj.table_map = self.table_map.copy()
        obj.join_map = self.join_map.copy()
        obj.rev_join_map = self.rev_join_map.copy()
        obj.quote_cache = {}
        obj.default_cols = self.default_cols
        obj.default_ordering = self.default_ordering
        obj.standard_ordering = self.standard_ordering
        obj.included_inherited_models = self.included_inherited_models.copy()
        obj.ordering_aliases = []
        obj.select_fields = self.select_fields[:]
        obj.related_select_fields = self.related_select_fields[:]
        obj.dupe_avoidance = self.dupe_avoidance.copy()
        obj.select = self.select[:]
        obj.tables = self.tables[:]
        obj.where = self.where.clone()
        obj.where_class = self.where_class
        if self.group_by is None:
            obj.group_by = None
        else:
            obj.group_by = self.group_by[:]
        obj.having = self.having.clone()
        obj.order_by = self.order_by[:]
        obj.low_mark, obj.high_mark = self.low_mark, self.high_mark
        obj.distinct = self.distinct
        obj.select_related = self.select_related
        obj.related_select_cols = []
        obj.aggregates = deepcopy(self.aggregates, memo=memo)
        if self.aggregate_select_mask is None:
            obj.aggregate_select_mask = None
        else:
            obj.aggregate_select_mask = self.aggregate_select_mask.copy()
        obj._aggregate_select_cache = None
        obj.max_depth = self.max_depth
        obj.extra = self.extra.copy()
        if self.extra_select_mask is None:
            obj.extra_select_mask = None
        else:
            obj.extra_select_mask = self.extra_select_mask.copy()
        if self._extra_select_cache is None:
            obj._extra_select_cache = None
        else:
            obj._extra_select_cache = self._extra_select_cache.copy()
        obj.extra_tables = self.extra_tables
        obj.extra_order_by = self.extra_order_by
        obj.deferred_loading = deepcopy(self.deferred_loading, memo=memo)
        if self.filter_is_sticky and self.used_aliases:
            obj.used_aliases = self.used_aliases.copy()
        else:
            obj.used_aliases = set()
        obj.filter_is_sticky = False
        obj.__dict__.update(kwargs)
        if hasattr(obj, '_setup_query'):
            obj._setup_query()
        return obj

    def _Node_clone(self):
        clone = self.__class__._new_instance( 
            children=[], connector=self.connector, negated=self.negated) 
        for child in self.children: 
            if isinstance(child, tuple): 
                clone.children.append( 
                    (child[0].clone(), child[1], child[2], child[3])) 
            else: 
                clone.children.append(child.clone()) 
        for parent in self.subtree_parents: 
            clone.subtree_parents.append(parent.clone()) 
        return clone 

    Aggregate.clone = _immutable_clone
    EverythingNode.clone = _immutable_clone
    NothingNode.clone = _immutable_clone
    ExtraWhere.clone = _immutable_clone
    Constraint.clone = _immutable_clone
    Query.clone = _Query_clone
    Node.clone = _Node_clone
